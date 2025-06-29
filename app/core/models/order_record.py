from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .base import BaseModel

__all__ = ["OrderRecord", "OrderLine"]


class OrderRecord(BaseModel):
    """Simple order record from ShipStation."""

    __tablename__ = "order_records"

    ext_id: Mapped[str] = mapped_column(db.String(50), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(db.String(50), nullable=False)
    status: Mapped[str] = mapped_column(db.String(20), nullable=False)
    currency: Mapped[str] = mapped_column(db.String(3), nullable=False, default="USD")
    total: Mapped[str] = mapped_column(db.String(20), nullable=False)
    placed_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    lines: Mapped[List["OrderLine"]] = relationship(
        "OrderLine", back_populates="order", cascade="all, delete-orphan"
    )


class OrderLine(BaseModel):
    """Line item in an order."""

    __tablename__ = "order_lines"

    order_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("order_records.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped["OrderRecord"] = relationship("OrderRecord", back_populates="lines")

    sku: Mapped[str] = mapped_column(db.String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
    unit_price: Mapped[str] = mapped_column(db.String(20), nullable=True)

