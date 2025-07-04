"""Organisation routes."""

from flask import Blueprint, jsonify

from inventory_manager_app.core.config.settings import settings

bp = Blueprint("organisation", __name__, url_prefix=settings.api_prefix)


@bp.route("/health")
def health() -> tuple[dict, int]:
    return jsonify({"status": "ok"}), 200
