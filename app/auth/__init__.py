"""Compatibility shim for deprecated imports.

Layer: api
"""

from app.api.auth import google_bp as google_blueprint

__all__ = ["google_blueprint"]
