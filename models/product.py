from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from .base import Base

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, nullable=False)
    title = Column(String)
    cost = Column(Numeric) 