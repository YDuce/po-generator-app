# app/core/models/organisation.py
from __future__ import annotations

from app.extensions import db

from .base import BaseModel


class Organisation(BaseModel):
    __tablename__ = "organisations"

    name = db.Column(db.String(255), unique=True, nullable=False)
    drive_folder_id = db.Column(db.String(256), unique=True, nullable=False)

    users = db.relationship(
        "User",
        back_populates="organisation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organisation {self.name}>"
