"""Celery periodic tasks schedule.

Layer: core
"""
from app.tasks.sync import SyncAllUsersOrders

beat_schedule = {
    "sync-orders-15m": {
        "task": SyncAllUsersOrders.name,
        "schedule": 900,  # seconds
    },
}
