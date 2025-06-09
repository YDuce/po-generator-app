"""Authentication service for token management.

Layer: core
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import jwt
from sqlalchemy.orm import Session

from app.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for token management."""

    def __init__(self, session: Session, secret_key: str):
        """Initialize auth service.
        
        Args:
            session: Database session
            secret_key: Secret key for JWT
        """
        self.session = session
        self.secret_key = secret_key

    def create_user(self, email: str, password: str) -> User:
        """Create a new user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User: Created user
            
        Raises:
            ValueError: If email is already taken
        """
        from app.services.auth import create_user
        return create_user(self.session, email, password)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Optional[User]: Authenticated user or None
        """
        from app.services.auth import authenticate
        return authenticate(self.session, email, password)

    def create_token(self, user: User) -> str:
        """Create a JWT token for a user.
        
        Args:
            user: User to create token for
            
        Returns:
            str: JWT token
        """
        payload = {
            "sub": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> Optional[User]:
        """Verify a JWT token and return the user.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Optional[User]: User if token is valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload["sub"]
            return self.session.query(User).get(user_id)
        except (jwt.InvalidTokenError, KeyError) as exc:
            logger.warning("invalid token: %s", exc)
            return None

    def revoke_token(self, token: str) -> None:
        """Revoke a JWT token.
        
        Args:
            token: JWT token to revoke
        """
        # In a real app, we would add the token to a blacklist
        # For now, we just verify it's valid
        self.verify_token(token) 