"""Authentication models."""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.models.base import BaseModel

class User(BaseModel):
    """User model."""
    __tablename__ = 'users'
    
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    # Relationships
    tokens = relationship('AuthToken', back_populates='user', cascade='all, delete-orphan')

class AuthToken(BaseModel):
    """Authentication token model."""
    __tablename__ = 'auth_tokens'
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    
    # Relationships
    user = relationship('User', back_populates='tokens') 