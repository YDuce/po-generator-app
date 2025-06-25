"""Thin synchronous wrapper around the ShipStation REST API."""
from __future__ import annotations

import base64
import logging
from typing import Any, Dict, List, Optional

import httpx

log = logging.getLogger(__name__)


class ShipStationClient:
    BASE_URL = "https://ssapi.shipstation.com"

    def __init__(self, key: str, secret: str, *, timeout: int = 15) -> None:
        token = base64.b64encode(f"{key}:{secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )

    # ───────────────────────── public API ─────────────────────────
    def list_orders(self, status: str = "awaiting_shipment") -> List[Dict[str, Any]]:
        """
        Return ShipStation orders as raw dicts.

        *status* defaults to ``awaiting_shipment`` which is the common polling
        state for fulfilment workflows.
        """
        resp = self._get("/orders", params={"orderStatus": status})
        return resp.json().get("orders", [])

    # ───────────────────────── internals ──────────────────────────
    def _get(
        self, path: str, *, params: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return resp

    # context-manager sugar (optional)
    def __enter__(self):  # pragma: no cover
        return self

    def __exit__(self, *_exc):  # pragma: no cover
        self._client.close()
