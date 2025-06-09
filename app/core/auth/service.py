"""Authentication service.

Layer: core
"""

import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
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
    
    def create_session(self, user: User, expires_in: int = 3600) -> Dict[str, Any]:
        """Create a new session for a user.
        
        Args:
            user: User to create session for
            expires_in: Session duration in seconds
            
        Returns:
            Dict containing session info
        """
        # Create JWT token
        token = self._create_jwt_token(user, expires_in)
        
        # Create session record
        session = Session(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        
        self.db.add(session)
        self.db.commit()
        
        logger.info(f"Created session for user {user.email}")
        return {
            'token': token,
            'expires_at': session.expires_at,
            'user': user.to_dict()
        }
    
    def validate_session(self, token: str) -> Optional[User]:
        """Validate a session token.
        
        Args:
            token: Session token to validate
            
        Returns:
            User if token is valid, None otherwise
        """
        try:
            # Validate JWT token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            
            # Get session from database
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
            
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error validating session: {str(e)}")
            return None
    
    def revoke_session(self, token: str) -> bool:
        """Revoke a session.
        
        Args:
            token: Session token to revoke
            
        Returns:
            True if session was revoked, False if not found
        """
        try:
            session = self.db.query(Session).filter_by(token=token).first()
            if not session:
                return False
                
            self.db.delete(session)
            self.db.commit()
            
            logger.info(f"Revoked session for user {session.user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error revoking session: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            expired = self.db.query(Session).filter(
                Session.expires_at < datetime.utcnow()
            ).all()
            
            count = len(expired)
            for session in expired:
                self.db.delete(session)
            
            self.db.commit()
            logger.info(f"Cleaned up {count} expired sessions")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {str(e)}")
            return 0
    
    def _create_jwt_token(self, user: User, expires_in: int) -> str:
        """Create a JWT token for a user.
        
        Args:
            user: User to create token for
            expires_in: Token expiration in seconds
            
        Returns:
            JWT token
        """
        payload = {
            'sub': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

def upsert_user(db_session, info):
    """Find or create a user from Google OAuth info."""
    email = info.get('email')
    if not email:
        raise ValueError('No email in Google user info')
        
    try:
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
        
    except Exception as e:
        logger.error(f"Error upserting user: {str(e)}")
        db_session.rollback()
        raise 