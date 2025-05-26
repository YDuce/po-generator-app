from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Allocation(Base):
    """Represents an allocation of inventory to a channel/listing."""
    __tablename__ = "allocation"

    id                = Column(Integer, primary_key=True)
    listing_id        = Column(Integer, ForeignKey("listing.id"), nullable=False)
    channel_id        = Column(Integer, ForeignKey("channel.id"), nullable=False)
    qty               = Column(Integer, nullable=False)
    priority          = Column(Integer, nullable=True)
    is_auto_allocated = Column(Boolean, default=True)
    status            = Column(String, default="pending")
    notes             = Column(Text, nullable=True)
    created_at        = Column(DateTime, server_default=func.now(), nullable=False)

    listing = relationship("Listing")
    channel = relationship("Channel") 