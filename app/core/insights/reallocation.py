"""Manage reallocation candidate list."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.models import MasterProduct, ReallocationCandidate

__all__ = ["ReallocationService"]


class ReallocationService:
    """Create and list reallocation candidates."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add_candidate(
        self, product: MasterProduct, *, from_channel: str, reason: str
    ) -> ReallocationCandidate:
        cand = ReallocationCandidate(
            product=product, from_channel=from_channel, reason=reason
        )
        self._db.add(cand)
        self._db.flush()
        return cand

    def all_candidates(self) -> list[ReallocationCandidate]:
        return (
            self._db.query(ReallocationCandidate)
            .order_by(ReallocationCandidate.created_at.desc())
            .all()
        )
