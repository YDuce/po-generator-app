from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Listing(Base):
    """Represents a product listing on a specific channel."""
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False)
    external_sku = Column(String, nullable=False)
    status = Column(String, nullable=False)
    price = Column(Numeric(10,2), nullable=False)
    cost = Column(Numeric(10,2), nullable=True)

    product = relationship("Product", back_populates="listings")
    channel = relationship("Channel", back_populates="listings")
    inventory_records = relationship("InventoryRecord", back_populates="listing")

    @property
    def current_quantity(self):
        if not self.inventory_records:
            return 0
        latest = max(self.inventory_records, key=lambda ir: ir.recorded_at)
        return latest.quantity 