"""Simple UI routes serving static files.

Layer: api
"""

from __future__ import annotations

from flask import Blueprint, current_app

bp = Blueprint("ui", __name__)


@bp.get("/")
def index():
    """Serve the single page application."""
    return current_app.send_static_file("index.html")
