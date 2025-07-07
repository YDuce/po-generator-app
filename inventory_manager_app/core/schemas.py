from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class OrderPayload(BaseModel):
    order_id: str
    channel: str
    product_sku: str
    quantity: int
    ordered_date: datetime | None = None
