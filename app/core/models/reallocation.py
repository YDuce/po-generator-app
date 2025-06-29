"""Reallocation candidate table."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .base import BaseModel
from .product import MasterProduct

__all__ = ["ReallocationCandidate"]


class ReallocationCandidate(BaseModel):
    __tablename__ = "reallocation_candidates"

    product_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey("master_products.id", ondelete="CASCADE"),
        nullable=False,
    )
    product: Mapped["MasterProduct"] = relationship(MasterProduct)

    from_channel: Mapped[str] = mapped_column(db.String(50), nullable=False)
    reason: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Realloc {self.product_id} from {self.from_channel}>"
