from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from sqlalchemy_utils import EmailType

from app.channels import ALLOWED_CHANNELS
from app.extensions import db
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(EmailType, unique=True, nullable=False, index=True)

    organisation_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False
    )
    organisation: Mapped["Organisation"] = relationship(back_populates="users")

    # -- SQLite friendly: plain JSON column, no JSONB / json_typeof() check
    allowed_channels: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list, server_default="[]"
    )

    @validates("allowed_channels")
    def _validate_allowed(self, _key: str, value: list[str]) -> list[str]:
        bad = set(value) - ALLOWED_CHANNELS
        if bad:
            raise ValueError(f"invalid channel(s): {', '.join(bad)}")
        return value

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"