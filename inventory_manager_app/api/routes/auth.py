"""Auth routes."""

from flask import Blueprint, jsonify, request, abort

from inventory_manager_app.core.models import User
from inventory_manager_app.core.utils.auth import (
    create_token,
    verify_password,
)
from inventory_manager_app.core.config.settings import get_settings

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
    token = create_token({"sub": user.id}, settings.secret_key)
    return jsonify({"token": token}), 200
