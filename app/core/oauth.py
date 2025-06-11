"""Google OAuth helpers.

Layer: core
"""
from __future__ import annotations

from flask import current_app, redirect
from flask_dance.contrib.google import make_google_blueprint, google

from app.core.auth.service import create_jwt_for_user, upsert_user

__all__ = ["init_oauth", "google"]


def init_oauth(app):
    """Register Google OAuth blueprint with callback."""
    google_bp = make_google_blueprint(
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        scope=["openid", "email", "profile"],
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    @google_bp.route("/authorized")
    def _authorized():
        resp = google.get("/oauth2/v2/userinfo")
        resp.raise_for_status()
        info = resp.json()
        user = upsert_user(app.extensions["db"].session, info)
        token = create_jwt_for_user(user)
        return redirect(f"{app.config['FRONTEND_URL']}?token={token}")
