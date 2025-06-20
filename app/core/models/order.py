"""Channel-independent order tables."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum, unique

from sqlalchemy import Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .base import BaseModel
from .product import MasterProduct


@unique
class Channel(str, Enum):
    WOOT = "woot"
    AMAZON = "amazon"
    EBAY = "ebay"
    OTHER = "other"


@unique
class OrderStatus(str, Enum):
    NEW = "new"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class OrderRecord(BaseModel):
    __tablename__ = "order_records"
    __table_args__ = (UniqueConstraint("channel", "ext_id", name="uix_channel_ext"),)

    ext_id: Mapped[str] = mapped_column(String(80), nullable=False)
    channel: Mapped[Channel] = mapped_column(db.Enum(Channel), nullable=False)

    placed_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[OrderStatus] = mapped_column(
        db.Enum(OrderStatus), default=OrderStatus.NEW, nullable=False
    )

    currency: Mapped[str] = mapped_column(String(4), default="USD")
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    lines: Mapped[list["OrderLine"]] = relationship(
        back_populates="order", cascade="all, delete-orphan", passive_deletes=True
    )

    def mark_shipped(self) -> None:
        self.status = OrderStatus.SHIPPED

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Order {self.channel.value}:{self.ext_id} {self.status}>"


class OrderLine(BaseModel):
    __tablename__ = "order_lines"

    order_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("order_records.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped["OrderRecord"] = relationship(back_populates="lines")

    product_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("master_products.id"), nullable=False
    )
    product: Mapped["MasterProduct"] = relationship()

    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<OrderLine {self.product_id} ×{self.quantity}>"
