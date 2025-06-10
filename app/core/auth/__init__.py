"""Authentication package utilities.

Layer: core
"""

from .service import AuthService  # noqa: F401
from .models import Session  # noqa: F401


def get_woot_service(*args, **kwargs):
    """Placeholder for woot service accessor used in routes."""
    raise NotImplementedError
