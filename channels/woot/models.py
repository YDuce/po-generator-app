from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from database import Base

class EventUploader(Base):
    __tablename__ = "woot_event_uploader"
    id = Column(Integer, primary_key=True)
    porf_id = Column(Integer, ForeignKey("porf.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False) 