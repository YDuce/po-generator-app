"""OAuth login endpoints.

Layer: api
"""

from __future__ import annotations

import os
from flask import Blueprint, redirect, url_for, jsonify, current_app, request
from flask_dance.contrib.google import make_google_blueprint, google

from app import db
from app.core.auth.service import AuthService

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_url="/api/auth/login/google",
)
bp.register_blueprint(google_bp, url_prefix="/login")


def _service() -> AuthService:
    return AuthService(db.session, current_app.config["SECRET_KEY"])


@bp.route("/login/google")
def login_google():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    data = resp.json()
    token = _service().upsert_user(data["id"], data["email"], data.get("name", ""))
    return jsonify({"token": token})


@bp.route("/me", methods=["GET"])
def get_current_user():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid authorization header"}), 401

    token = auth_header.split(" ")[1]
    user = _service().verify_token(token)
    if not user:
        return jsonify({"error": "Invalid token"}), 401
    return jsonify(user.to_dict())


@bp.route("/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Invalid authorization header"}), 401
    token = auth_header.split(" ")[1]
    _service().revoke_token(token)
    return jsonify({"message": "Logged out"})
