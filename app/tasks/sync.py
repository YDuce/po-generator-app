"""Celery tasks for periodic synchronisation."""
from __future__ import annotations

import os

from celery import Task
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db, celery_app
from app.core.logic.orders import OrderSyncService
from app.channels import import_channel, get_adapter

# ---------------------------------------------------------------------------
# Enable / disable adapters per environment:
#   SYNC_CHANNELS=woot,amazon  (comma-separated, no spaces)
#   defaults to "woot" if unset.
# ---------------------------------------------------------------------------

_ENABLED = [name for name in os.getenv("SYNC_CHANNELS", "woot").split(",") if name]

for _name in _ENABLED:
    import_channel(_name)  # registers adapter via decorator


def _sync_adapter(name: str) -> int:
    session = db.session
    logic = OrderSyncService(session)
    adapter = get_adapter(name)

    count = 0
    for payload in adapter.fetch_orders():
        logic.upsert(payload)
        count += 1

    try:
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    return count


@celery_app.task(name="sync.orders", bind=True)
def sync_orders(self: Task) -> None:  # pragma: no cover
    total = sum(_sync_adapter(name) for name in _ENABLED)
    self.get_logger().info("orders synced", extra={"count": total})


# Beat schedule remains unchanged (optional)
celery_app.conf.beat_schedule.setdefault(
    "sync-orders-every-15m",
    {"task": "sync.orders", "schedule": 900},
)
