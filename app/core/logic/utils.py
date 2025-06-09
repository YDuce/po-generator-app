"""Utility helpers for core logic.

Layer: core
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

__all__ = ["add_months", "slugify"]


def add_months(dt: datetime, months: int) -> datetime:
    """Return ``dt`` shifted by ``months`` months."""
    return dt + relativedelta(months=months)


def slugify(label: str, identifier: int | str) -> str:
    """Return a hyphenated lowercase slug for Drive items."""
    return f"{label.lower()}-{identifier}"
