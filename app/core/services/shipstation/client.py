# app/integrations/shipstation/client.py
from __future__ import annotations

import base64
import logging
from typing import Any, Dict, List, Optional

import httpx

log = logging.getLogger(__name__)


class ShipStationClient:
    BASE = "https://ssapi.shipstation.com"

    def __init__(self, key: str, secret: str, *, timeout: int = 15) -> None:
        auth = base64.b64encode(f"{key}:{secret}".encode()).decode()
        self._headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}
        self._client = httpx.Client(base_url=self.BASE, headers=self._headers, timeout=timeout)

    # -------------------------------- public API

    def list_orders(self, status: str = "awaiting_shipment") -> List[Dict[str, Any]]:
        resp = self._get("/orders", params={"orderStatus": status})
        return resp.json()["orders"]

    # -------------------------------- internals

    def _get(self, path: str, *, params: Optional[Dict[str, str]] = None) -> httpx.Response:
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return resp
