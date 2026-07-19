"""User store: email/password auth + Stripe subscription status + usage caps.

Deliberately minimal (no ORM migrations, no admin panel) — this is the data
layer for an MVP with a handful of early users, not a scaled product.

DATABASE_URL defaults to a local SQLite file, which is fine for local
development but gets wiped on every redeploy on hosts with an ephemeral
filesystem (e.g. Render's free tier) — point it at a managed Postgres
before relying on this for real users (see DEPLOY.md). Render's Postgres
connection strings use the `postgres://` scheme, which SQLAlchemy 1.4+
rejects; normalized to `postgresql://` below so either works untouched.

Password hashing uses stdlib pbkdf2_hmac rather than a bcrypt dependency —
no compiled C-extension to worry about across deploy targets.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./sowld.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

MONTHLY_SEARCH_LIMIT = int(os.environ.get("MONTHLY_SEARCH_LIMIT", "50"))

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_status = Column(String, nullable=False, default="none")  # none | active | canceled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    search_count = Column(Integer, nullable=False, default=0)
    search_period_start = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def is_subscribed(self) -> bool:
        return self.subscription_status == "active"


def init_db() -> None:
    Base.metadata.create_all(engine)


def try_consume_search(user_id: int) -> bool:
    """Check the user's monthly search cap and consume one search if under it.

    Caps the worst-case Anthropic API spend per subscriber to a predictable
    amount regardless of how heavily they use the search — the subscription
    price only covers a bounded number of searches, not unlimited usage.
    Resets on a rolling 30-day window from the first search of the period,
    not the calendar month, so it doesn't need a scheduled job to reset.
    """
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if not user:
            return False

        now = datetime.now(timezone.utc)
        period_start = user.search_period_start
        if period_start and period_start.tzinfo is None:
            period_start = period_start.replace(tzinfo=timezone.utc)
        if not period_start or (now - period_start).days >= 30:
            user.search_period_start = now
            user.search_count = 0

        if user.search_count >= MONTHLY_SEARCH_LIMIT:
            db.commit()
            return False

        user.search_count += 1
        db.commit()
        return True
    finally:
        db.close()


def _hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}${digest.hex()}"


def hash_password(password: str) -> str:
    return _hash_password(password, secrets.token_bytes(16))


def verify_password(password: str, stored: str) -> bool:
    salt_hex, _, _ = stored.partition("$")
    salt = bytes.fromhex(salt_hex)
    return hmac.compare_digest(_hash_password(password, salt), stored)
