# app/core/models/organisation.py
from __future__ import annotations

from sqlalchemy import CheckConstraint

from app.extensions import db

from .base import BaseModel


class Organisation(BaseModel):
    __tablename__ = "organisations"

    name = db.Column(db.String(255), unique=True, nullable=False)
    drive_folder_id = db.Column(db.String(256), unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint(
            "length(drive_folder_id) >= 25",
            name="ck_drive_folder_id_format",
        ),
    )

    users = db.relationship(
        "User",
        back_populates="organisation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organisation {self.name}>"


__all__ = ["Organisation"]
