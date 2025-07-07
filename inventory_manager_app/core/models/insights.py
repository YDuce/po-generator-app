from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .product import Product

from .base import Base


class Insight(Base):
    __tablename__ = "insight"  # type: ignore[assignment]

    product_sku: Mapped[str] = mapped_column(
        ForeignKey("product.sku"), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    generated_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    product: Mapped["Product"] = relationship(back_populates="insights")
