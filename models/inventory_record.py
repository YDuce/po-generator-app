from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base

class InventoryRecord(Base):
    __tablename__ = 'inventory_record'
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey('listing.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, server_default=func.current_timestamp()) 