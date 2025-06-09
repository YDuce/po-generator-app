"""Authentication service.

Layer: core
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from flask import current_app
from sqlalchemy.orm import Session as DBSession
from werkzeug.security import generate_password_hash, check_password_hash
from app.core.auth.models import Session
from app.core.models.user import User

logger = logging.getLogger(__name__)

class AuthService:
    """Authentication service for managing users and sessions."""
    
    def __init__(self, db_session: DBSession, secret_key: str):
        """Initialize auth service.
        
        Args:
            db_session: SQLAlchemy database session
            secret_key: Application secret key for token generation
        """
        self.db = db_session
        self.secret_key = secret_key
    
    def create_session(self, user: User, expires_in: int = 3600) -> Session:
        """Create a new session for a user.
        
        Args:
            user: User to create session for
            expires_in: Session duration in seconds
            
        Returns:
            Created session
        """
        # Generate token
        token = self._generate_token(user)
        
        # Create session
        session = Session(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        
        self.db.add(session)
        self.db.commit()
        
        logger.info(f"Created session for user {user.email}")
        return session
    
    def validate_session(self, token: str) -> Optional[User]:
        """Validate a session token.
        
        Args:
            token: Session token to validate
            
        Returns:
            User if token is valid, None otherwise
        """
        session = self.db.query(Session).filter_by(token=token).first()
        if not session:
            return None
            
        if session.expires_at < datetime.utcnow():
            self.db.delete(session)
            self.db.commit()
            return None
            
        # Update last activity
        session.last_activity = datetime.utcnow()
        self.db.commit()
        
        return session.user
    
    def revoke_session(self, token: str) -> bool:
        """Revoke a session.
        
        Args:
            token: Session token to revoke
            
        Returns:
            True if session was revoked, False if not found
        """
        session = self.db.query(Session).filter_by(token=token).first()
        if not session:
            return False
            
        self.db.delete(session)
        self.db.commit()
        
        logger.info(f"Revoked session for user {session.user.email}")
        return True
    
    def _generate_token(self, user: User) -> str:
        """Generate a session token.
        
        Args:
            user: User to generate token for
            
        Returns:
            Generated token
        """
        # Use a combination of user ID, timestamp, and secret key
        timestamp = datetime.utcnow().timestamp()
        token_data = f"{user.id}:{timestamp}:{self.secret_key}"
        return self._hash_token(token_data)
    
    def _hash_token(self, token_data: str) -> str:
        """Hash a token.
        
        Args:
            token_data: Token data to hash
            
        Returns:
            Hashed token
        """
        import hashlib
        return hashlib.sha256(token_data.encode()).hexdigest()

def upsert_user(db_session, info):
    """Find or create a user from Google OAuth info."""
    email = info.get('email')
    if not email:
        raise ValueError('No email in Google user info')
    user = db_session.query(User).filter_by(email=email).first()
    if user:
        # Update user info if changed
        updated = False
        if 'first_name' in info and user.first_name != info['first_name']:
            user.first_name = info['first_name']
            updated = True
        if 'last_name' in info and user.last_name != info['last_name']:
            user.last_name = info['last_name']
            updated = True
        if 'name' in info and (not user.first_name or not user.last_name):
            # Try to split name if first/last missing
            parts = info['name'].split(' ', 1)
            if len(parts) == 2:
                user.first_name, user.last_name = parts
                updated = True
        if updated:
            db_session.commit()
        return user
    # Create new user
    user = User(
        email=email,
        first_name=info.get('given_name') or info.get('first_name'),
        last_name=info.get('family_name') or info.get('last_name'),
    )
    db_session.add(user)
    db_session.commit()
    return user 