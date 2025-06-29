import hmac
import json
import logging
from hashlib import sha256
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ShipStationWebhookError(Exception):
    """Raised when a webhook payload fails verification."""


def verify_signature(secret: str, payload: bytes, signature: str) -> bool:
    """Verify ShipStation webhook signature."""
    digest = hmac.new(secret.encode(), payload, sha256).hexdigest()
    return hmac.compare_digest(digest, signature)


def parse_order_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract order information from webhook payload."""
    order = {
        "order_id": str(data.get("orderId")),
        "channel": data.get("advancedOptions", {}).get("storeId") or data.get("marketplace"),
        "items": [
            {
                "sku": item.get("sku"),
                "quantity": int(item.get("quantity", 0)),
                "unit_price": item.get("unitPrice"),
            }
            for item in data.get("items", [])
        ],
        "status": data.get("orderStatus", "unknown"),
        "total": str(data.get("orderTotal", "0")),
        "currency": data.get("orderCurrency", "USD"),
        "created_at": data.get("orderDate") or data.get("createDate"),
    }
    return order


def process_webhook(payload: bytes, secret: str, signature: str) -> Dict[str, Any]:
    """Validate and parse ShipStation webhook payload."""
    if not verify_signature(secret, payload, signature):
        logger.warning("ShipStation signature mismatch")
        raise ShipStationWebhookError("invalid signature")
    data = json.loads(payload.decode())
    return parse_order_payload(data)
