from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.extensions import db


class BaseModel(db.Model):  # type: ignore[misc]
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Helpers ----------------------------------------------------------------

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            elif isinstance(val, Decimal):
                val = str(val)
            out[c.name] = val
        return out