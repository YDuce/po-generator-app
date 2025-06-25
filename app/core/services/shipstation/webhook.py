"""
Helpers to verify & parse ShipStation webhook payloads.

Importing this module has *no* side effects; it can be used by both
Flask routes and background tasks.
"""
from __future__ import annotations

import hmac
import json
from hashlib import sha256
from typing import Any, Dict


def verify_signature(secret: str, payload: bytes, header_sig: str) -> bool:
    """Return ``True`` if *header_sig* matches the HMAC-SHA256 of *payload*."""
    digest = hmac.new(secret.encode(), payload, sha256).hexdigest()
    return hmac.compare_digest(digest, header_sig.lower())


def parse_webhook(payload: bytes) -> Dict[str, Any]:
    """Decode the JSON payload delivered by ShipStation."""
    return json.loads(payload.decode())
