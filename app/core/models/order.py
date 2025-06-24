from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.channels import Channel  # single source of truth
from app.extensions import db
from .base import BaseModel


class OrderRecord(BaseModel):
    __tablename__ = "orders"

    external_id: Mapped[str] = mapped_column(db.String(60), unique=True, nullable=False)
    channel: Mapped[Channel] = mapped_column(db.Enum(Channel), nullable=False)
    total: Mapped[Decimal] = mapped_column(db.Numeric(scale=2), nullable=False)
    ordered_at: Mapped[datetime] = mapped_column(db.DateTime(timezone=True), nullable=False)

    lines: Mapped[list["OrderLine"]] = relationship("OrderLine", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order {self.channel}:{self.external_id}>"


class OrderLine(BaseModel):
    __tablename__ = "order_lines"

    order_id: Mapped[int] = mapped_column(db.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    sku: Mapped[str] = mapped_column(db.String(120), nullable=False)
    qty: Mapped[int] = mapped_column(db.Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(db.Numeric(scale=2), nullable=False)

    order: Mapped[OrderRecord] = relationship("OrderRecord", back_populates="lines")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OrderLine {self.order_id}:{self.sku} x{self.qty}>"