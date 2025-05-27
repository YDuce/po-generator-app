from sqlalchemy import Column, Integer, String
from database import Base
from models.base import JSONB

class Product(Base):
    """Represents a product/SKU in the catalog."""
    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, nullable=False)
    asin = Column(String, unique=True, nullable=True)
    core_attrs = Column(JSONB, nullable=True) 