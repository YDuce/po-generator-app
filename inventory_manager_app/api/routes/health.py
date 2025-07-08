from flask import Blueprint
from flask.typing import ResponseReturnValue


bp = Blueprint("health", __name__, url_prefix="/api/v1")


def health() -> ResponseReturnValue:
    return {"status": "ok"}, 200


bp.add_url_rule("/health", view_func=health, methods=["GET"])


__all__ = ["bp"]
