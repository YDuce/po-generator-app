"""
Pure domain layer – *no* Flask, Celery, or external SDKs.

Everything here is synchronous, deterministic, and side-effect-free
(except for SQLAlchemy persistence through an injected Session).
"""

from .models.base import BaseModel
from .logic.inventory import InventoryService
from .logic.orders import OrderSyncService, OrderPayload, OrderLinePayload

__all__ = [
    # models
    "BaseModel",
    # logic services
    "InventoryService",
    "OrderSyncService",
    "OrderPayload",
    "OrderLinePayload",
]