# app/core/models/user.py
from __future__ import annotations

from app.extensions import db

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    google_id = db.Column(db.String(64), unique=True)

    organisation_id = db.Column(
        db.Integer,
        db.ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
    )
    organisation = db.relationship("Organisation", back_populates="users")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.email}>"
