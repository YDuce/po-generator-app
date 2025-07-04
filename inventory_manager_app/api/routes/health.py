from flask import Blueprint
from inventory_manager_app.core.config.settings import settings


bp = Blueprint("health", __name__, url_prefix=settings.api_prefix)


@bp.route("/health", methods=["GET"])
def health() -> tuple[dict, int]:
    return {"status": "ok"}, 200


__all__ = ["bp"]
