from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, func
from database import Base
import enum


class PORFStatus(enum.Enum):
    draft = "draft"
    approved = "approved"
    expired = "expired"


class POStatus(enum.Enum):
    open = "open"
    expired = "expired"


class EventUploader(Base):
    __tablename__ = "woot_event_uploader"
    id = Column(Integer, primary_key=True)
    porf_id = Column(Integer, ForeignKey("porf.id"), nullable=False)
    category = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
