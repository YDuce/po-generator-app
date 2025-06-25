from __future__ import annotations
from typing import Any

from sqlalchemy import Index, String, JSON, text as sa_text  # ← JSON instead of JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .base import BaseModel


class MasterProduct(BaseModel):
    __tablename__ = "master_products"
    __table_args__ = (
        Index("ix_master_products_sku", "sku"),
        # extra_data GIN index removed – not supported on SQLite
    )

    sku: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    inventory_records: Mapped[list["InventoryRecord"]] = relationship(
        "InventoryRecord",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    order_lines: Mapped[list["OrderLine"]] = relationship(
        "OrderLine", back_populates="product", viewonly=True
    )


class InventoryRecord(BaseModel):
    __tablename__ = "inventory_records"

    product_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("master_products.id", ondelete="CASCADE"), nullable=False
    )
    product: Mapped["MasterProduct"] = relationship(back_populates="inventory_records")

    quantity_delta: Mapped[int] = mapped_column(db.Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1_000))
    extra_data: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, server_default="{}"  # ← JSON + simple default
    )

    def __repr__(self) -> str:  # pragma: no cover
        sign = "+" if self.quantity_delta >= 0 else ""
        return f"<InventoryRecord {sign}{self.quantity_delta} {self.source}>"
