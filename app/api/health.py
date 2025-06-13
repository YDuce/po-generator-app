from flask import Blueprint

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    return {"status": "ok"}, 200
