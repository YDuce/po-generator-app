from __future__ import annotations

import json
import logging
import os
from logging.config import dictConfig
from pathlib import Path
from typing import Final

import structlog
from flask import Flask
from google.oauth2 import service_account
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .api import auth_bp, health_bp, organisation_bp
from .config import CONFIG_MAP
from .core.auth.oauth import init_oauth
from .extensions import cors, db, init_celery, migrate
from channels.woot.routes import bp as woot_bp
from app.startup import preload_adapters
preload_adapters()

__all__ = ["create_app"]

_LOGGING_CONFIG: Final = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
        }
    },
    "handlers": {
        "default": {"class": "logging.StreamHandler", "formatter": "plain", "level": "INFO"}
    },
    "root": {"level": "INFO", "handlers": ["default"]},
}

_LOGGING_SETUP_DONE = False


def _configure_logging() -> None:
    global _LOGGING_SETUP_DONE
    if _LOGGING_SETUP_DONE:
        return
    dictConfig(_LOGGING_CONFIG)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO), cache_logger_on_first_use=True
    )
    _LOGGING_SETUP_DONE = True


def create_app(env: str | None = None) -> Flask:
    _configure_logging()

    app = Flask(__name__, instance_relative_config=True)

    env_name = (env or os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development").lower()
    cfg_obj = CONFIG_MAP[env_name]()  # instantiate so each app gets its own copy
    app.config.from_object(cfg_obj)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    if (raw := os.getenv("GOOGLE_SVC_KEY")):
        key_data = json.loads(Path(raw).read_text()) if Path(raw).is_file() else json.loads(raw)
        creds = service_account.Credentials.from_service_account_info(
            key_data,
            scopes=[
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
            ],
        )
        app.config["GOOGLE_SVC_CREDS"] = creds

    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):

        @event.listens_for(Engine, "connect")
        def _fk_pragma(conn, _):  # noqa: D401
            conn.execute("PRAGMA foreign_keys=ON")

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    init_celery(app)
    init_oauth(app)

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(organisation_bp, url_prefix="/api/organisation")
    app.register_blueprint(woot_bp, url_prefix="/api/woot")

    return app
