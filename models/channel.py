from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Channel(Base):
    """Represents a sales channel (e.g., Amazon, eBay)."""
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

    listings = relationship("Listing", back_populates="channel") 