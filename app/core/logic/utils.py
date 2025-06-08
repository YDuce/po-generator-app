"""Utility helpers for core logic.

Layer: core
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta

__all__ = ["add_months"]


def add_months(dt: datetime, months: int) -> datetime:
    """Return ``dt`` shifted by ``months`` months."""
    return dt + relativedelta(months=months)
