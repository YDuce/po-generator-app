# app/integrations/shipstation/webhook.py
"""
Helpers to verify & parse ShipStation webhook payloads.
"""

import hmac
import json
from hashlib import sha256
from typing import Any, Dict


def verify_signature(secret: str, payload: bytes, header_sig: str) -> bool:
    digest = hmac.new(secret.encode(), payload, sha256).hexdigest()
    return hmac.compare_digest(digest, header_sig.lower())


def parse_webhook(payload: bytes) -> Dict[str, Any]:
    return json.loads(payload.decode())
