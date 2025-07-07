"""Re-export all API route blueprints here for clean imports."""

from .auth import bp as auth_bp
from .health import bp as health_bp
from .organisation import bp as organisation_bp
from .reallocation import bp as reallocation_bp
from .webhook import bp as webhook_bp

__all__ = [
    "auth_bp",
    "organisation_bp",
    "webhook_bp",
    "reallocation_bp",
    "health_bp",
]
