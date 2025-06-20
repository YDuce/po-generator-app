# app/integrations/shipstation/__init__.py
"""
ShipStation HTTP client + webhook → domain events.

This package purposefully contains **no** SQLAlchemy imports.
"""

from .client import ShipStationClient
from .webhook import parse_webhook

__all__ = ["ShipStationClient", "parse_webhook"]
