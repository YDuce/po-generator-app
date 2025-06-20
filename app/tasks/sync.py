# app/tasks/sync.py
# Celery tasks for periodic synchronisation

from __future__ import annotations
from celery import Task

from app.extensions import db, celery_app
from app.core.logic.orders import OrderSyncService
from channels.woot.service import WootAdapter

@celery_app.task(name="sync.woot_orders", bind=True)
def sync_woot_orders(self: Task) -> None:  # pragma: no cover
    adapter = WootAdapter()
    session = db.session
    logic = OrderSyncService(session)

    for raw in adapter.fetch_orders():
        logic.upsert(raw)

    session.commit()
    self.get_logger().info("woot orders synced", extra={"count": len(adapter.fetch_orders())})