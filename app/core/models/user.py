from __future__ import annotations

from sqlalchemy import CheckConstraint, text as sa_text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.channels import ALLOWED_CHANNELS
from app.extensions import db
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(db.String(255))
    first_name: Mapped[str | None] = mapped_column(db.String(120))
    last_name: Mapped[str | None] = mapped_column(db.String(120))

    allowed_channels: Mapped[list[str]] = mapped_column(
        db.JSON, nullable=False, default=list, server_default=sa_text("'[]'::jsonb")
    )

    organisations: Mapped[list["Organisation"]] = relationship(
        "Organisation", secondary="organisation_members", back_populates="members"
    )

    __table_args__ = (
        # ensure JSON is an array; rely on validator for element validity
        CheckConstraint(
            "jsonb_typeof(allowed_channels) = 'array'",
            name="ck_user_allowed_channels_array",
        ),
    )

    # ---------------------------------------------------------------------

    @validates("allowed_channels")
    def _validate_allowed(self, _key: str, value: list[str]) -> list[str]:
        bad = set(value) - ALLOWED_CHANNELS
        if bad:
            raise ValueError(f"invalid channel(s): {', '.join(bad)}")
        return value

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"