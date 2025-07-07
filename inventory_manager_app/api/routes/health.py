from flask import Blueprint


bp = Blueprint("health", __name__, url_prefix="/api/v1")


@bp.route("/health", methods=["GET"])  # type: ignore[misc]
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


__all__ = ["bp"]
