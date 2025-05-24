from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class SalesOrder(Base):
    __tablename__ = 'sales_order'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False)
    external_id = Column(String, unique=True, nullable=False)
    placed_at = Column(DateTime)
    status = Column(String)
    order_lines = relationship('OrderLine', back_populates='sales_order') 