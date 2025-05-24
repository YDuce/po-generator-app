from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class OrderLine(Base):
    __tablename__ = 'order_line'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('sales_order.id'), nullable=False)
    listing_id = Column(Integer, ForeignKey('listing.id'), nullable=False)
    qty = Column(Integer, nullable=False)
    sales_order = relationship('SalesOrder', back_populates='order_lines') 