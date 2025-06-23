"""Aggregate blueprints so `app/__init__.py` can import once."""
from flask import Blueprint

from .auth import bp as auth_bp
from .health import bp as health_bp
from .organisation import bp as organisation_bp

__all__ = ["auth_bp", "health_bp", "organisation_bp"]
