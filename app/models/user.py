"""
User model for authentication and authorization.
"""

from flask_login import UserMixin
from app import db
from app.core.models.base import Base

class User(Base, UserMixin):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    
    # OAuth token storage
    oauth_token = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @property
    def current_user(self):
        """Get the current user from Flask-Login."""
        from flask_login import current_user
        return current_user

    def to_dict(self) -> dict:
        """Convert user to dictionary.
        
        Returns:
            dict: User data
        """
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        } 