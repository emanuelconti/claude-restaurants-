"""SQLite-backed user store: email/password auth + Stripe subscription status.

Deliberately minimal (no ORM migrations, no admin panel) — this is the data
layer for an MVP with a handful of early users, not a scaled product. Swap
DATABASE_URL for a managed Postgres once there's real traffic; SQLAlchemy
makes that a one-line change.

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

    @property
    def is_subscribed(self) -> bool:
        return self.subscription_status == "active"


def init_db() -> None:
    Base.metadata.create_all(engine)


def _hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return f"{salt.hex()}${digest.hex()}"


def hash_password(password: str) -> str:
    return _hash_password(password, secrets.token_bytes(16))


def verify_password(password: str, stored: str) -> bool:
    salt_hex, _, _ = stored.partition("$")
    salt = bytes.fromhex(salt_hex)
    return hmac.compare_digest(_hash_password(password, salt), stored)
