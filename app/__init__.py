# app/__init__.py
from __future__ import annotations

import json
import logging
import os
import sys

from dotenv import load_dotenv
from flask import Flask
from google.oauth2 import service_account

from .api.auth import bp as auth_bp
from .api.health import bp as health_bp
from .api.organisation import bp as organisation_bp
from config import config
from .core.oauth import init_oauth
from .extensions import db, migrate, cors


def _google_creds() -> service_account.Credentials:
    raw = os.getenv("GOOGLE_SVC_KEY")
    if not raw:
        sys.exit("GOOGLE_SVC_KEY missing — aborting.")
    try:
        key_dict = json.loads(raw)
    except json.JSONDecodeError:
        sys.exit("GOOGLE_SVC_KEY is not valid JSON.")
    return service_account.Credentials.from_service_account_info(
        key_dict,
        scopes=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ],
    )


def create_app(env: str | None = None) -> Flask:
    load_dotenv()                                # moved inside the factory
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    app = Flask(__name__, instance_relative_config=True)

    env = env or os.getenv("FLASK_ENV", "development")
    try:
        app.config.from_object(config[env])
    except KeyError:
        sys.exit("Unknown FLASK_ENV '{env}'")

    app.config["GOOGLE_SVC_CREDS"] = _google_creds()

    # Flask-SQLAlchemy / Alembic
    db.init_app(app)
    migrate.init_app(app, db)

    # CORS (safe default to '*')
    origins = app.config.get("CORS_ORIGINS", "*")
    cors.init_app(app, resources={r"/*": {"origins": origins}})

    init_oauth(app)

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(organisation_bp, url_prefix="/api/organisation")

    return app