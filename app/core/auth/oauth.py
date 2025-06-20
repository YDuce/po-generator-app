from flask import Flask, current_app, redirect, session
from flask_dance.consumer import oauth_authorized
from flask_dance.contrib.google import make_google_blueprint, google
from google.oauth2.credentials import Credentials

from app.core.auth.service import create_jwt_for_user, upsert_user

def init_oauth(app: Flask) -> None:
    google_bp = make_google_blueprint(
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        scope=["openid", "email", "profile"],
        offline=True,
    )
    app.register_blueprint(google_bp, url_prefix="/login")

    @oauth_authorized.connect_via(google_bp)
    def on_google_login(_, token: dict | None):
        if not token:
            return False
        resp = google.get("/oauth2/v2/userinfo")
        resp.raise_for_status()
        user = upsert_user(current_app.extensions["db"].session, resp.json())
        session["google_token"] = token
        jwt_token = create_jwt_for_user(user)
        return redirect(f"{current_app.config['FRONTEND_URL']}?token={jwt_token}")

def get_user_creds() -> Credentials:
    tok = session.get("google_token", {})
    return Credentials(
        token=tok.get("access_token"),
        refresh_token=tok.get("refresh_token"),
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
    )
