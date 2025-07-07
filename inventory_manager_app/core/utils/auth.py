"""JWT helpers."""

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional

from flask import abort, g, request
from functools import wraps

from inventory_manager_app.core.config.settings import get_settings

import jwt
from werkzeug.security import check_password_hash, generate_password_hash


def create_token(payload: dict[str, Any], secret: str, expires_in: int = 86400) -> str:
    now = datetime.now(timezone.utc)
    to_encode = payload | {"exp": now + timedelta(seconds=expires_in), "iat": now}
    return jwt.encode(to_encode, secret, algorithm="HS256")


def verify_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, hash_: str) -> bool:
    return check_password_hash(hash_, password)


def require_auth(role: Optional[str] = None) -> Callable:
    """Decorator enforcing JWT auth and optional role check."""

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                abort(401)
            token = header.split()[1]
            try:
                settings = get_settings()
                payload = verify_token(token, settings.secret_key)
            except jwt.InvalidTokenError:
                abort(401)
            user_id = payload.get("sub")
            from inventory_manager_app.core.models import User
            from inventory_manager_app.extensions import db

            user = db.session.get(User, user_id)
            if user is None:
                abort(401)

            user_roles: list[str] = []
            if hasattr(user, "role") and getattr(user, "role"):
                user_roles = [getattr(user, "role")]
            elif hasattr(user, "allowed_channels") and user.allowed_channels:
                user_roles = list(user.allowed_channels)

            if role and role not in user_roles:
                abort(403)
            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator
