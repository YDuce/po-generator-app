"""PORF CSV → canonical OrderPayload."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from typing import Iterable

import requests
from pydantic import ValidationError

from app.channels import ChannelAdapter, register
from app.core.logic.orders import OrderPayload, OrderLinePayload, Channel, OrderStatus

_CSV_URL = "https://woot-bucket.s3.amazonaws.com/today_porfs.csv"  # placeholder


@register("woot")
class WootAdapter(ChannelAdapter):
    """Downloads PORF CSV and yields `OrderPayload`s."""

    def fetch_orders(self) -> Iterable[OrderPayload]:
        text = self._download_csv()
        for row in csv.DictReader(text.splitlines()):
            try:
                yield self._row_to_payload(row)
            except ValidationError as exc:  # pragma: no cover
                # log & skip bad rows
                print("invalid row", exc)

    # ---------------------------------------------------------------- internals

    @staticmethod
    def _download_csv() -> str:
        resp = requests.get(_CSV_URL, timeout=30)
        resp.raise_for_status()
        return resp.text

    @staticmethod
    def _row_to_payload(row: dict[str, str]) -> OrderPayload:
        placed_at = datetime.strptime(row["OrderDate"], "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        line = OrderLinePayload(
            sku=row["SKU"],
            quantity=int(row["Quantity"]),
            unit_price=row["UnitPrice"],
        )
        return OrderPayload(
            ext_id=row["OrderID"],
            channel=Channel.WOOT,
            placed_at=placed_at,
            status=OrderStatus.NEW,
            currency=row.get("Currency", "USD"),
            total=row["OrderTotal"],
            lines=[line],
        )
