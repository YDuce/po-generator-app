"""
Public facade for ShipStation integration.

No SQLAlchemy or Flask imports here – this package is pure I/O.
"""

from .client import ShipStationClient
from .webhook import parse_webhook, verify_signature

__all__ = ["ShipStationClient", "parse_webhook", "verify_signature"]
