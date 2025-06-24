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

    def as_dict(self) -> dict[str, Any]:  # pragma: no cover (mostly for admin dumps)
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # Decimal → str so JSON dumps cleanly
    @staticmethod
    def jsonify(val: Any) -> Any:  # pragma: no cover
        if isinstance(val, Decimal):
            return str(val)
        if isinstance(val, datetime):
            return val.isoformat()
        return val