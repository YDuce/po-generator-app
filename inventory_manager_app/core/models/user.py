from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .organisation import Organisation

from .base import Base


class User(Base):
    __tablename__ = "user"  # type: ignore[assignment]
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    organisation_id: Mapped[int] = mapped_column(
        ForeignKey("organisation.id"), nullable=False, index=True
    )
    organisation: Mapped["Organisation"] = relationship(back_populates="users")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    allowed_channels: Mapped[list[str]] = mapped_column(JSON, default=list)
