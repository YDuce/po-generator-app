# app/tasks/__init__.py
"""
Celery application shared by Flask and workers.

Workers import the instance defined in `app.extensions`, so there is exactly
one connection pool and one task registry.
"""
from __future__ import annotations

from app.extensions import celery_app  # re-export

__all__ = ["celery_app"]
