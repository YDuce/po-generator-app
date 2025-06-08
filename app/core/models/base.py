"""Base model for all database models."""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, String, Boolean

Base = declarative_base()

class TimestampMixin:
    """Mixin that adds created_at and updated_at columns."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class BaseModel(Base, TimestampMixin):
    """Base model with common fields and methods."""
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True, nullable=False)
    external_id = Column(String(255), unique=True, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary.
        
        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary.
        
        Args:
            data: Dictionary containing model data
            
        Returns:
            Model instance
        """
        return cls(**data) 