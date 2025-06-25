"""
Celery singleton & beat-schedule wiring.
"""

from app.extensions import celery_app

# ── periodic tasks ---------------------------------------------------------
from .beat import beat_schedule

celery_app.conf.beat_schedule.update(beat_schedule)

# ── task registration (execute decorators) ---------------------------------
import app.tasks.sync  # noqa: F401  ensures SyncAllUsersOrders is registered

__all__ = ["celery_app"]