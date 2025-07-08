"""Auth routes."""

from flask import Blueprint, Response, abort, jsonify, request
from pydantic import ValidationError

from inventory_manager_app.core.utils.validation import abort_json

from inventory_manager_app.core.config.settings import get_settings
from inventory_manager_app.core.models import User
from inventory_manager_app.core.utils.auth import create_token, verify_password
from inventory_manager_app.core.schemas import LoginPayload

bp = Blueprint("auth", __name__, url_prefix="/api/v1")


@bp.route("/login", methods=["POST"])
def login() -> tuple[Response, int]:
    try:
        login_data = LoginPayload.model_validate(request.json or {})
    except ValidationError as e:
        abort_json(400, str(e))
    user = User.query.filter_by(email=login_data.email).first()
    if user is None or not verify_password(login_data.password, user.password_hash):
        abort(401)
    settings = get_settings()
    payload = {
        "sub": user.id,
        "org_id": user.organisation_id,
        "roles": user.allowed_channels or ["user"],
    }
    token = create_token(payload, settings.secret_key)
    return jsonify({"token": token}), 200
