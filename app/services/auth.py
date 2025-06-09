"""Authentication service module.

Layer: service
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User

logger = logging.getLogger(__name__)


def upsert_user(session: Session, info: Dict[str, Any]) -> User:
    """Create or update a user from OAuth info.
    
    Args:
        session: Database session
        info: User info from OAuth provider
        
    Returns:
        User: Created or updated user
    """
    email = info.get("email")
    if not email:
        raise ValueError("email is required")

    user = session.query(User).filter_by(email=email).first()
    if user:
        # Update existing user
        user.name = info.get("name", user.name)
        user.picture = info.get("picture", user.picture)
        session.commit()
        return user

    # Create new user
    user = User(
        email=email,
        name=info.get("name", ""),
        picture=info.get("picture", ""),
        password_hash=generate_password_hash("")  # Empty password for OAuth users
    )
    session.add(user)
    session.commit()
    return user


def create_user(session: Session, email: str, password: str, name: str = "") -> User:
    """Create a new user.
    
    Args:
        session: Database session
        email: User email
        password: User password
        name: User name
        
    Returns:
        User: Created user
        
    Raises:
        ValueError: If email is already taken
    """
    if session.query(User).filter_by(email=email).first():
        raise ValueError("email already taken")

    user = User(
        email=email,
        name=name,
        password_hash=generate_password_hash(password)
    )
    session.add(user)
    session.commit()
    return user


def authenticate(session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user.
    
    Args:
        session: Database session
        email: User email
        password: User password
        
    Returns:
        Optional[User]: Authenticated user or None
    """
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return None

    if not user.password_hash:
        return None  # OAuth user

    if not check_password_hash(user.password_hash, password):
        return None

    return user 