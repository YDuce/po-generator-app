"""Authentication service."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import Session
from app.core.auth.models import User, AuthToken

class AuthService:
    """Service for handling authentication."""
    
    def __init__(self, db: Session, secret_key: str):
        """Initialize the auth service.
        
        Args:
            db: Database session
            secret_key: Secret key for JWT tokens
        """
        self.db = db
        self.secret_key = secret_key
    
    def create_user(self, email: str, password: str, **kwargs) -> User:
        """Create a new user.
        
        Args:
            email: User email
            password: User password
            **kwargs: Additional user attributes
            
        Returns:
            Created user
        """
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = self.db.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        return None
    
    def create_token(self, user: User, expires_in: int = 3600) -> str:
        """Create a JWT token for a user.
        
        Args:
            user: User to create token for
            expires_in: Token expiration time in seconds
            
        Returns:
            JWT token
        """
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token_data = {
            'user_id': user.id,
            'email': user.email,
            'exp': expires_at.timestamp()
        }
        token = jwt.encode(token_data, self.secret_key, algorithm='HS256')
        
        # Store token in database
        auth_token = AuthToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        self.db.add(auth_token)
        self.db.commit()
        
        return token
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            User if token is valid, None otherwise
        """
        try:
            # Check if token is revoked
            auth_token = self.db.query(AuthToken).filter_by(token=token).first()
            if not auth_token or auth_token.is_revoked:
                return None
            
            # Verify token
            data = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            user = self.db.query(User).get(data['user_id'])
            return user
        except jwt.InvalidTokenError:
            return None
    
    def revoke_token(self, token: str) -> None:
        """Revoke a JWT token.
        
        Args:
            token: Token to revoke
        """
        auth_token = self.db.query(AuthToken).filter_by(token=token).first()
        if auth_token:
            auth_token.is_revoked = True
            self.db.commit() 