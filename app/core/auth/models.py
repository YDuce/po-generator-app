"""Authentication models.

Layer: core
"""
from __future__ import annotations

from app.extensions import db
from app.core.models.base import BaseModel

__all__ = ["User"]

class User(BaseModel):
    __tablename__ = "users"

    email            = db.Column(db.String, unique=True, nullable=False)
    password_hash    = db.Column(db.String, nullable=True)
    first_name       = db.Column(db.String)
    last_name        = db.Column(db.String)
    google_id        = db.Column(db.String, unique=True)
    organisation_id  = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False)
    organisation     = db.relationship("Organisation", backref="users")

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "email":             self.email,
            "first_name":        self.first_name,
            "last_name":         self.last_name,
            "google_id":         self.google_id,
            "organisation_id":   self.organisation_id,
        }
