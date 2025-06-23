"""PORF draft tables (Woot-specific, optional)."""
from __future__ import annotations

from enum import Enum, unique

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base import BaseModel
from app.core.models.product import MasterProduct
from app.extensions import db


@unique
class PorfStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"


class WootPorf(BaseModel):
    __tablename__ = "woot_porfs"

    porf_no: Mapped[str] = mapped_column(db.String(64), unique=True, nullable=False)
    status: Mapped[PorfStatus] = mapped_column(
        db.Enum(PorfStatus), default=PorfStatus.DRAFT
    )

    lines: Mapped[list["WootPorfLine"]] = relationship(
        back_populates="porf", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WootPorf {self.porf_no} {self.status}>"


class WootPorfLine(BaseModel):
    __tablename__ = "woot_porf_lines"

    porf_id: Mapped[int] = mapped_column(
        db.Integer, ForeignKey("woot_porfs.id", ondelete="CASCADE"), nullable=False
    )
    porf: Mapped["WootPorf"] = relationship(back_populates="lines")

    product_id: Mapped[int] = mapped_column(
        db.Integer,
        ForeignKey("master_products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product: Mapped["MasterProduct"] = relationship(MasterProduct)

    quantity: Mapped[int] = mapped_column(db.Integer, nullable=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<WootPorfLine {self.product_id} ×{self.quantity}>"
