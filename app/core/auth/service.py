"""Authentication helpers and services.

Layer: core
"""
from __future__ import annotations

import jwt
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from app.core.auth.models import User

__all__ = ["create_jwt_for_user", "upsert_user", "AuthService"]


def create_jwt_for_user(user: User) -> str:
    """Generate a JWT for the given user."""
    now = datetime.utcnow()
    exp = now + current_app.config["JWT_EXPIRATION"]
    payload = {
        "user_id": user.id,
        "email": user.email,
        "iat": now,
        "exp": exp,
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def upsert_user(db_session, info: dict) -> User:
    """Create or update a User record from Google OAuth info."""
    email = info.get("email")
    user = db_session.query(User).filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            first_name=info.get("given_name"),
            last_name=info.get("family_name"),
            google_id=info.get("id"),
        )
        db_session.add(user)
    else:
        user.first_name = info.get("given_name", user.first_name)
        user.last_name = info.get("family_name", user.last_name)
    db_session.commit()
    return user


class AuthService:
    """Service for basic email/password authentication."""

    def __init__(self, db_session):
        self.db = db_session

    def create_user(self, email: str, password: str) -> User:
        """
        Create a new user with a hashed password.
        Raises an exception if the email is already taken.
        """
        if self.db.query(User).filter_by(email=email).first():
            raise ValueError(f"Email '{email}' is already registered")
        hashed = generate_password_hash(password)
        user = User(email=email, password_hash=hashed)
        self.db.add(user)
        self.db.commit()
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        """
        Verify credentials and return the User if valid, else None.
        """
        user = self.db.query(User).filter_by(email=email).first()
        if not user or not user.password_hash:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user
