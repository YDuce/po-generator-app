from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Batch(Base):
    """Represents a Woot batch (purchase order)."""
    __tablename__ = 'woot_batch'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    lines = relationship('BatchLine', back_populates='batch', cascade='all, delete-orphan')

class BatchLine(Base):
    """Represents a line in a Woot batch (one SKU/qty)."""
    __tablename__ = 'woot_batch_line'
    id = Column(Integer, primary_key=True)
    batch_id = Column(Integer, ForeignKey('woot_batch.id'), nullable=False)
    listing_id = Column(Integer, ForeignKey('listing.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    batch = relationship('Batch', back_populates='lines')
    listing = relationship('Listing')
