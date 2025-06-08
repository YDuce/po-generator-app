"""Core product models for the application."""

from sqlalchemy import Column, String, JSON, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.models.base import BaseModel


class MasterProduct(BaseModel):
    """Master product model."""

    __tablename__ = "master_products"

    sku = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    extra_data = Column(JSON)

    # Relationships
    inventory_records = relationship(
        "InventoryRecord", back_populates="product", cascade="all, delete-orphan"
    )


class InventoryRecord(BaseModel):
    """Inventory record model."""

    __tablename__ = "inventory_records"

    product_id = Column(Integer, ForeignKey("master_products.id"), nullable=False)
    quantity_delta = Column(
        Integer, nullable=False
    )  # Positive for additions, negative for removals
    source = Column(String(50), nullable=False)  # e.g., 'manual', 'woot', 'amazon'
    notes = Column(String(500))
    extra_data = Column(JSON)

    # Relationships
    product = relationship("MasterProduct", back_populates="inventory_records")
