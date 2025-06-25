from __future__ import annotations

import logging
import os
from typing import Optional

from celery import Task
from sqlalchemy.exc import SQLAlchemyError

from app.channels import ALLOWED_CHANNELS, get_adapter, import_channel
from app.core.logic.orders import OrderSyncService
from app.core.models.user import User
from app.extensions import celery_app, db

log = logging.getLogger(__name__)


# ───────────────────── adapter preload helper ─────────────────────
def init_sync_channels(env_var: Optional[str] = None) -> None:
    raw = env_var or os.getenv("SYNC_CHANNELS", ",".join(ALLOWED_CHANNELS))
    for name in filter(None, raw.split(",")):
        try:
            import_channel(name)
        except ModuleNotFoundError:
            log.warning("SYNC_CHANNELS lists '%s' but adapter not deployed", name)


# ─────────────────────────── celery task ───────────────────────────
class SyncAllUsersOrders(Task):
    name = "sync.all_users_orders"
    max_retries = 0

    def run(self) -> None:  # type: ignore[override]
        total = 0
        try:
            for user in db.session.query(User).all():
                for ch in user.allowed_channels:
                    try:
                        adapter = get_adapter(ch)
                    except ValueError:
                        log.info("User %s has unknown/disabled channel '%s'", user.id, ch)
                        continue

                    logic = OrderSyncService(db.session)
                    for payload in adapter.fetch_orders():
                        logic.upsert(payload, user=user)
                        total += 1

            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise
        finally:
            db.session.remove()

        self.get_logger().info("orders synced", extra={"count": total})


celery_app.register_task(SyncAllUsersOrders())