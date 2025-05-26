from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class InventoryRecord(Base):
    """Represents a time-stamped inventory snapshot for a listing."""
    __tablename__ = "inventory_record"
    id          = Column(Integer, primary_key=True)
    listing_id  = Column(Integer, ForeignKey("listing.id"), nullable=False)
    quantity    = Column(Integer, nullable=False)
    recorded_at = Column(DateTime, server_default=func.now(), nullable=False)

    listing = relationship("Listing", back_populates="inventory_records") 