"""Read-model helpers (pure functions)."""
from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.models.order import Channel, OrderRecord


def daily_order_counts(db: Session, *, since: date) -> list[dict[str, Any]]:
    rows = (
        db.query(
            func.date(OrderRecord.placed_at).label("day"),
            OrderRecord.channel,
            func.count().label("cnt"),
        )
        .filter(OrderRecord.placed_at >= since)
        .group_by("day", OrderRecord.channel)
        .all()
    )
    return [{"day": d.isoformat(), "channel": ch.value, "count": c} for d, ch, c in rows]


def top_skus(db: Session, *, limit: int = 10) -> list[dict[str, Any]]:
    sql = """
        SELECT p.sku, SUM(l.quantity) AS qty
          FROM order_lines l
          JOIN master_products p ON p.id = l.product_id
      GROUP BY p.sku
      ORDER BY qty DESC
         LIMIT :limit
    """
    rows = db.execute(sql, {"limit": limit}).fetchall()
    return [{"sku": r[0], "quantity": r[1]} for r in rows]
