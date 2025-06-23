from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.extensions import db


class BaseModel(db.Model):  # type: ignore[misc]
    """Common auto-id and timestamp mix-in."""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.__class__.__name__} id={self.id}>"

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for col in self.__table__.columns:  # type: ignore[attr-defined]
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                out[col.name] = val.isoformat()
            elif isinstance(val, Decimal):
                out[col.name] = str(val)
            else:
                out[col.name] = val
        return out
