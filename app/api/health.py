from flask import Blueprint, jsonify

bp = Blueprint("health", __name__, url_prefix="/health")


@bp.get("")
def health():
    return jsonify({"status": "ok"}), 200
