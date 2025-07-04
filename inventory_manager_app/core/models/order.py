from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product

from .base import Base


class OrderRecord(Base):
    __tablename__ = "order_record"

    order_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    product_sku: Mapped[str] = mapped_column(ForeignKey("product.sku"), nullable=False)
    quantity: Mapped[int] = mapped_column()
    ordered_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    product: Mapped["Product"] = relationship(back_populates="orders")
