from __future__ import annotations

from sqlalchemy import CheckConstraint, text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.channels import ALLOWED_CHANNELS
from app.extensions import db
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        db.String(255), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str | None] = mapped_column(db.String(255))
    first_name: Mapped[str | None] = mapped_column(db.String(120))
    last_name: Mapped[str | None] = mapped_column(db.String(120))

    allowed_channels: Mapped[list[str]] = mapped_column(
        db.JSON, nullable=False, default=list, server_default="[]"
    )

    organisation_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
    )
    organisation: Mapped["Organisation"] = relationship(back_populates="users")

    __table_args__ = (
        db.Index(
            "ix_users_allowed_channels_gin",
            "allowed_channels",
            postgresql_using="gin",
        ),
    )

    @validates("allowed_channels")
    def _validate_allowed(self, _key: str, value: list[str]) -> list[str]:  # noqa: D401
        bad = set(value) - ALLOWED_CHANNELS
        if bad:
            raise ValueError(f"invalid channel(s): {', '.join(bad)}")
        return value

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"


__all__ = ["User"]
