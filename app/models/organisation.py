from app.core.models.base import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

class Organisation(Base):
    __tablename__ = 'organisations'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    workspace_folder_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 