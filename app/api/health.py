"""Health check endpoint.

Layer: api
"""
from flask import Blueprint, jsonify

bp = Blueprint("health", __name__)


@bp.get("/health")
def health() -> tuple[dict, int]:
    """Return service health status."""
    return {"status": "ok"}, 200

__all__ = ["bp"]
