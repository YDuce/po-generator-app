"""Database model for inventory reallocations."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Reallocation(Base):
    """Product reallocation entry between channels."""

    __tablename__ = "reallocation"
    __table_args__ = (
        UniqueConstraint(
            "sku", "channel_origin", "reason", name="uq_reallocation_sku_chan_reason"
        ),
    )

    sku: Mapped[str] = mapped_column(
        ForeignKey("product.sku", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    channel_origin: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    added_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<Reallocation sku={self.sku} channel={self.channel_origin} "
            f"reason={self.reason}>"
        )
