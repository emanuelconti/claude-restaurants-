"""Session helpers built on Starlette's signed-cookie sessions."""

from __future__ import annotations

from fastapi import Request

from .db import SessionLocal, User


def get_current_user(request: Request) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    db = SessionLocal()
    try:
        return db.get(User, user_id)
    finally:
        db.close()


def login(request: Request, user: User) -> None:
    request.session["user_id"] = user.id


def logout(request: Request) -> None:
    request.session.pop("user_id", None)
