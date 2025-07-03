"""JWT helpers."""

from datetime import datetime, timedelta, timezone
from typing import Any

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
