from __future__ import annotations
from flask import Flask, current_app, redirect, session
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.google import make_google_blueprint, google
from google.oauth2.credentials import Credentials
from flask.typing import ResponseReturnValue

from app.core.auth.service import create_jwt_for_user, upsert_user


def init_oauth(app: Flask) -> None:
    google_bp = make_google_blueprint(
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        scope=["openid","email","profile"],
        offline=True,
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    @oauth_authorized.connect_via(google_bp)
    def _on_login(bp: object, token: dict | None) -> ResponseReturnValue | bool:
        if not token:
            return False
        info = google.get("/oauth2/v2/userinfo").json()
        user = upsert_user(app.extensions["db"].session, info)
        session["google_token"] = token
        jwt_token = create_jwt_for_user(user)
        return redirect(f"{app.config['FRONTEND_URL']}?token={jwt_token}")


def get_user_creds() -> Credentials:
    tok = session.get("google_token", {})
    return Credentials(
        token=tok.get("access_token"),
        refresh_token=tok.get("refresh_token"),
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
    )
