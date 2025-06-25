"""Idempotent upsert of raw channel orders."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Mapping, Sequence, Union

from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.models.order import Channel, OrderLine, OrderRecord, OrderStatus
from app.core.models.product import MasterProduct


# ────────────────────── canonical payload ──────────────────────


class OrderLinePayload(BaseModel):
    sku: str
    quantity: int = Field(..., gt=0)
    unit_price: str  # keep as string to preserve decimal precision


class OrderPayload(BaseModel):
    ext_id: str
    channel: Channel
    placed_at: datetime
    status: OrderStatus
    currency: str = "USD"
    total: str
    lines: Sequence[OrderLinePayload]

    @field_validator("placed_at", mode="before")
    @classmethod
    def _ensure_utc(cls, v):  # noqa: ANN001
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


# ───────────────────────── service ────────────────────────────


class OrderSyncService:
    """Upsert orders + lines in a single transaction."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def upsert(self, payload: Union[Mapping, OrderPayload]) -> OrderRecord:
        data = payload.model_dump() if isinstance(payload, BaseModel) else payload

        order = (
            self._db.query(OrderRecord)
            .filter_by(ext_id=data["ext_id"], channel=data["channel"])
            .one_or_none()
        )

        if order is None:
            order = OrderRecord(
                ext_id=data["ext_id"],
                channel=data["channel"],
                placed_at=data.get("placed_at", datetime.now(timezone.utc)),
                status=data.get("status", OrderStatus.NEW),
                currency=data.get("currency", "USD"),
                total=Decimal(data["total"]),
            )
            self._db.add(order)
            self._db.flush()

            for ln in data["lines"]:
                ln_dict = ln if isinstance(ln, dict) else ln.model_dump()
                prod = self._db.query(MasterProduct).filter_by(sku=ln_dict["sku"]).one()
                self._db.add(
                    OrderLine(
                        order=order,
                        product=prod,
                        quantity=int(ln_dict["quantity"]),
                        unit_price=Decimal(ln_dict["unit_price"]),
                    )
                )
        else:
            order.status = data.get("status", order.status)
            order.total = Decimal(data["total"])

        return order
