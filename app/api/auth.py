import logging
from functools import wraps

import jwt
from flask import Blueprint, current_app, jsonify, request

from app.core.auth.service import AuthService, create_jwt_for_user
from app.core.models.user import User
from app.extensions import db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
log = logging.getLogger(__name__)


def _token_required(fn):
    @wraps(fn)
    def _wrap(*args, **kwargs):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            user = db.session.get(User, payload["user_id"])
            if not user:
                raise ValueError
        except Exception:  # noqa: BLE001
            return jsonify({"error": "unauthorized"}), 401
        return fn(user, *args, **kwargs)

    return _wrap


# ─────────────────────────── routes ────────────────────────────


@bp.post("/register")
def register():
    data = request.get_json() or {}
    email, password = data.get("email", "").strip(), data.get("password", "")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    try:
        user = AuthService(db.session).create_user(email, password)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409
    token = create_jwt_for_user(user)
    return jsonify({"token": token, "user": user.to_dict()}), 201


@bp.post("/login")
def login():
    data = request.get_json() or {}
    email, password = data.get("email", "").strip(), data.get("password", "")
    user = AuthService(db.session).authenticate(email, password)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    token = create_jwt_for_user(user)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@bp.post("/refresh")
@_token_required
def refresh(user: User):  # type: ignore[valid-type]
    return jsonify({"token": create_jwt_for_user(user)}), 200


@bp.get("/me")
@_token_required
def me(user: User):  # type: ignore[valid-type]
    return jsonify(user.to_dict()), 200
