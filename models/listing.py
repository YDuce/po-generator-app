from sqlalchemy import Column, Integer, String, ForeignKey
from .base import Base

class Listing(Base):
    __tablename__ = 'listing'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False)
    external_sku = Column(String)
    status = Column(String) 