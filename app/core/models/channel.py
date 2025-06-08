"""Core channel models for the application."""

from sqlalchemy import Column, String, JSON
from app.core.models.base import BaseModel

class Channel(BaseModel):
    """Channel model."""
    __tablename__ = 'channels'
    
    name = Column(String(50), unique=True, nullable=False)
    type = Column(String(50), nullable=False)  # e.g., 'woot', 'amazon'
    config = Column(JSON)  # Channel-specific configuration
    extra_data = Column(JSON) 