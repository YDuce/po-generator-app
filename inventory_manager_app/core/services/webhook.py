"""ShipStation webhook handling."""

import hashlib
import hmac
import time
from typing import Any


class WebhookService:
    """Validate ShipStation webhooks with replay protection."""

    def __init__(self, secrets: list[str], window_seconds: int = 300) -> None:
        self.secrets = secrets
        self.window = window_seconds
        self._recent: dict[str, float] = {}

    def verify(self, payload: bytes, signature: str) -> bool:
        now = time.time()
        if signature in self._recent and now - self._recent[signature] < self.window:
            return False
        for secret in self.secrets:
            digest = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
            if hmac.compare_digest(digest, signature):
                self._recent[signature] = now
                return True
        return False

    def process(self, data: dict[str, Any]) -> None:
        """Placeholder processor."""
        return None
