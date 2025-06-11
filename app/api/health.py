"""Health check endpoint.

Layer: api
"""
from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)
__all__ = ["bp"]

@bp.get("/health")
def health() -> tuple[dict, int]:
    """Return service health status."""
    return {"status": "ok"}, 200

@bp.get("/")
def root_health() -> tuple[dict, int]:
    """Alias root URL to health status."""
    return {"status": "ok"}, 200
