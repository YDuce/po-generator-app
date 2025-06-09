"""User model."""

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
    is_active = Column(Boolean, default=True)
    company_name = Column(String(255))
    company_address = Column(String(512))
    phone = Column(String(50))
    
    # Relationships
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan') 