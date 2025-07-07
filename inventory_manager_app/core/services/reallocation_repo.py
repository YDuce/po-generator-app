"""Repository helpers for `Reallocation` persistence."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Reallocation


class ReallocationRepository:
    """Data access helper for `Reallocation` rows."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Reallocation]:
        return self.db.query(Reallocation).order_by(Reallocation.added_date).all()

    def list_paginated(self, *, page: int = 1, size: int = 50) -> list[Reallocation]:
        offset = (page - 1) * size
        return (
            self.db.query(Reallocation)
            .order_by(Reallocation.added_date)
            .offset(offset)
            .limit(size)
            .all()
        )

    def exists(self, sku: str, channel_origin: str, reason: str) -> bool:
        return (
            self.db.query(Reallocation)
            .filter_by(sku=sku, channel_origin=channel_origin, reason=reason)
            .first()
            is not None
        )

    def create(self, sku: str, channel_origin: str, reason: str) -> Reallocation:
        realloc = Reallocation(
            sku=sku,
            channel_origin=channel_origin,
            reason=reason,
        )
        self.db.add(realloc)
        self.db.flush()
        self.db.refresh(realloc)
        return realloc
