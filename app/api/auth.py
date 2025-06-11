"""Authentication API endpoints.

Layer: api
"""
from __future__ import annotations

import jwt
from functools import wraps

from flask import Blueprint, current_app, jsonify, request

from app.extensions import db
from app.core.auth.models import User
from app.core.auth.service import AuthService, create_jwt_for_user

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
__all__ = ["bp", "token_required"]


def token_required(f):
    """Decorator enforcing JWT authentication."""

    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "")
        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            user = User.query.get(payload["user_id"])
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return f(user, *args, **kwargs)

    return wrapper


@bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    service = AuthService(db.session)
    try:
        user = service.create_user(email, password)
        token = create_jwt_for_user(user)
        return jsonify({"token": token, "user": user.to_dict()}), 201
    except Exception as exc:  # pragma: no cover - basic error
        return jsonify({"error": str(exc)}), 400


@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    service = AuthService(db.session)
    user = service.authenticate(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_jwt_for_user(user)
    return jsonify({"token": token, "user": user.to_dict()}), 200


@bp.post("/refresh")
@token_required
def refresh_token(user: User):
    token = create_jwt_for_user(user)
    return jsonify({"token": token}), 200


@bp.get("/me")
@token_required
def get_current_user(user: User):
    return jsonify(user.to_dict()), 200
