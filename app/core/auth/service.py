"""Password + OAuth helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Final

import jwt
from flask import current_app
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.models.user import User

_ALG: Final = "HS256"


# ───────────────────────── JWT helpers ──────────────────────────
def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_jwt_for_user(user: User) -> str:
    cfg = current_app.config
    payload = {
        "user_id": user.id,
        "iat": _now(),
        "exp": _now() + cfg.get("JWT_EXPIRATION", timedelta(days=1)),
    }
    return jwt.encode(payload, cfg["JWT_SECRET"], algorithm=_ALG)  # type: ignore[return-value]


# ──────────────────────── user helpers ──────────────────────────
def upsert_user(session: Session, info: dict, *, default_org_id: int | None = 1) -> User:
    """Insert or update a user row from Google user-info."""
    user = session.query(User).filter_by(email=info["email"]).one_or_none()
    if user is None:
        user = User(
            email=info["email"],
            first_name=info.get("given_name"),
            last_name=info.get("family_name"),
            google_id=info.get("id"),
            organisation_id=default_org_id,
        )
        session.add(user)
    else:
        user.first_name = info.get("given_name", user.first_name)
        user.last_name = info.get("family_name", user.last_name)
        user.google_id = info.get("id", user.google_id)
    session.flush()  # id available to caller
    return user


# ───────────────────────── AuthService ─────────────────────────
class AuthService:
    """Password-based auth plus helpers."""

    def __init__(self, session: Session, *, default_org_id: int | None = 1) -> None:
        self._db = session
        self._default_org_id = default_org_id

    # ---------- password users ----------
    def create_user(self, email: str, password: str) -> User:
        if self._db.query(User).filter_by(email=email).first():
            raise ValueError("email already registered")
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            organisation_id=self._default_org_id,
        )
        self._db.add(user)
        self._db.commit()
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self._db.query(User).filter_by(email=email).first()
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            return user
        return None
