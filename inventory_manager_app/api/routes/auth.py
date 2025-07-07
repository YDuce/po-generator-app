"""Auth routes."""

from flask import Blueprint, abort, jsonify, request

from inventory_manager_app.core.config.settings import get_settings
from inventory_manager_app.core.models import User
from inventory_manager_app.core.utils.auth import create_token, verify_password

bp = Blueprint("auth", __name__, url_prefix="/api/v1")


@bp.route("/login", methods=["POST"])
def login() -> tuple[dict, int]:
    data = request.json or {}
    email = data.get("email")
    password = data.get("password", "")
    if not email or not password:
        abort(400, description="Missing credentials")
    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        abort(401)
    settings = get_settings()
    payload = {
        "sub": user.id,
        "org_id": user.organisation_id,
        "roles": user.allowed_channels or ["user"],
    }
    token = create_token(payload, settings.secret_key)
    return jsonify({"token": token}), 200
