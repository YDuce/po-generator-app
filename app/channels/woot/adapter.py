from typing import List, Dict
from app.core.models.order import Channel, OrderStatus
from googleapiclient.discovery import build

class WootAdapter:
    def fetch_orders(self) -> List[Dict]:
        # call API / parse CSV …
        yield {
            "ext_id": "WOOT-123",
            "channel": Channel.WOOT,
            "placed_at": parsed_dt,
            "status": OrderStatus.NEW,
            "currency": "USD",
            "total": "29.99",
            "lines": [
                {"sku": "ABC-1", "quantity": 3, "unit_price": "9.99"},
            ],
        }
