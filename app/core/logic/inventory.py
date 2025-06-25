"""Pure, side-effect-free stock-mutation helpers."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.models.product import InventoryRecord, MasterProduct


class InventoryService:
    """Aggregate root for stock-on-hand calculations."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ───────────────────── writes ──────────────────────
    def adjust(
            self,
            product: MasterProduct,
            delta: int,
            *,
            source: str,
            notes: str | None = None,
            when: datetime | None = None,
    ) -> InventoryRecord:
        rec = InventoryRecord(
            product=product,
            quantity_delta=delta,
            source=source,
            notes=notes,
            created_at=when or datetime.now(timezone.utc),
        )
        self._db.add(rec)
        self._db.flush()  # id available to caller
        return rec

    # ───────────────────── reads ───────────────────────
    def current_qty(self, product: MasterProduct) -> int:
        stmt = (
            select(func.coalesce(func.sum(InventoryRecord.quantity_delta), 0))
            .where(InventoryRecord.product_id == product.id)
        )
        return self._db.scalar(stmt)

    def history(self, product: MasterProduct) -> Sequence[InventoryRecord]:
        return (
            self._db.query(InventoryRecord)
            .filter_by(product_id=product.id)
            .order_by(InventoryRecord.created_at.desc())
            .all()
        )
