"""API package."""

from app.api.health import bp as health_bp
from app.api.auth import bp as auth_bp

__all__ = ['health_bp', 'auth_bp']
