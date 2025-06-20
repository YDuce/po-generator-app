# app/core/__init__.py
"""
Core – pure domain layer.

No Flask, Celery or Google APIs may be imported from this package.
Everything here must be synchronous, deterministic and side-effect free
(except for SQLAlchemy persistence through injected `session` objects).
"""

# Export common interfaces for type-checkers
from .models.base import BaseModel

__all__ = ["BaseModel"]
