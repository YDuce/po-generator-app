from __future__ import annotations

import os

from celery import Task
from sqlalchemy.exc import SQLAlchemyError

from app.channels import import_channel, get_adapter, ALLOWED_CHANNELS
from app.core.logic.orders import OrderSyncService
from app.core.models.user import User
from app.extensions import celery_app, db

for _name in os.getenv("SYNC_CHANNELS", ",".join(ALLOWED_CHANNELS)).split(","):
    if not _name:
        continue
    try:
        import_channel(_name)
    except ModuleNotFoundError:  # channel package not yet deployed
        continue


def _sync_user(user: User) -> int:
    """Return count of orders upserted for *user*."""
    logic = OrderSyncService(db.session)
    count = 0

    for name in user.allowed_channels:
        try:
            adapter = get_adapter(name)
        except ValueError:
            # channel disabled or not deployed – skip cleanly
            continue

        for payload in adapter.fetch_orders():
            logic.upsert(payload)
            count += 1

    return count


@celery_app.task(name="sync.all_users_orders", bind=True)
def sync_all_users_orders(self: Task) -> None:  # pragma: no cover
    total = 0
    try:
        users = db.session.query(User).all()
        for u in users:
            total += _sync_user(u)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    finally:
        db.session.remove()

    self.get_logger().info("orders synced", extra={"count": total})


# Optional beat schedule -----------------------------------------------------
celery_app.conf.beat_schedule.setdefault(
    "sync-orders-15m", {"task": "sync.all_users_orders", "schedule": 900}
)
