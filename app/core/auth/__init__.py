"""
Public façade for auth helpers so callers
can simply:

    from app.core.auth import AuthService, create_jwt_for_user, init_oauth

"""

from .service import AuthService, create_jwt_for_user, upsert_user
from .oauth import init_oauth, get_user_creds

__all__ = [
    "AuthService",
    "create_jwt_for_user",
    "upsert_user",
    "init_oauth",
    "get_user_creds",
]
