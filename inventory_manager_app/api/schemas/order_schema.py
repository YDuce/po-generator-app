"""Order schema."""

from datetime import datetime
from pydantic import BaseModel


class OrderSchema(BaseModel):
    order_id: str
    channel: str
    product_sku: str
    quantity: int
    ordered_date: datetime

    class Config:
        from_attributes = True
