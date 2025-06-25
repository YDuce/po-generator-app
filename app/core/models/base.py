from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):  # type: ignore[misc]  SQLA 2.x base
    __abstract__ = True

    # ─── common columns ──────────────────────────────────────────
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        server_onupdate=func.now(),
        nullable=False,
    )

    # ─── helpers ─────────────────────────────────────────────────
    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for col in self.__table__.columns:  # type: ignore[attr-defined]
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            elif isinstance(val, Decimal):
                val = str(val)
            out[col.name] = val
        return out

    # legacy alias
    def to_dict(self) -> dict[str, Any]:  # pragma: no cover
        return self.as_dict()