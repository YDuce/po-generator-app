"""Idempotent upsert of raw channel orders."""
from __future__ import annotations

from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.models.order import (
    Channel,
    OrderLine,
    OrderRecord,
    OrderStatus,
)
from app.core.models.product import MasterProduct


class OrderSyncService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def upsert(self, payload: dict) -> OrderRecord:
        order = (
            self._db.query(OrderRecord)
            .filter_by(ext_id=payload["ext_id"], channel=payload["channel"])
            .one_or_none()
        )

        if order is None:
            order = OrderRecord(
                ext_id=payload["ext_id"],
                channel=Channel(payload["channel"]),
                placed_at=payload.get("placed_at", datetime.utcnow()),
                status=OrderStatus(payload.get("status", OrderStatus.NEW)),
                currency=payload.get("currency", "USD"),
                total=Decimal(payload["total"]),
            )
            self._db.add(order)
            self._db.flush()

            for line in payload["lines"]:
                prod = (
                    self._db.query(MasterProduct)
                    .filter_by(sku=line["sku"])
                    .one()
                )
                self._db.add(
                    OrderLine(
                        order=order,
                        product=prod,
                        quantity=int(line["quantity"]),
                        unit_price=Decimal(line["unit_price"]),
                    )
                )
        else:
            order.status = OrderStatus(payload.get("status", order.status))
            order.total = Decimal(payload["total"])

        return order
