"""User model."""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.core.models.base import BaseModel

class User(BaseModel, UserMixin):
    """User model."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    company_name = db.Column(db.String(255))
    company_address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    google_id = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth relationships
    oauth_tokens = db.relationship('OAuth', back_populates='user', lazy='dynamic')
    sessions = db.relationship('Session', back_populates='user', lazy='dynamic')
    
    def set_password(self, password: str) -> None:
        """Set user password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check user password."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'company_name': self.company_name,
            'company_address': self.company_address,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 