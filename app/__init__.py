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

# ─── adapter preload (every process) ─────────────────────────────
from app.tasks.preload import preload_adapters

preload_adapters()

# Celery-side preload (once)
from app.tasks.sync import init_sync_channels

init_sync_channels()

# Blueprints defined AFTER registry is filled
from app.channels.woot.routes import bp as woot_bp  # noqa: E402

__all__ = ["create_app"]

# ─────────────── structured logging config ───────────────────────
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
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )
    _LOGGING_SETUP_DONE = True


# ─────────────────────────── factory ──────────────────────────────
def create_app(env: str | None = None) -> Flask:
    _configure_logging()

    app = Flask(__name__, instance_relative_config=True)

    env_name = (env or os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development").lower()
    app.config.from_object(CONFIG_MAP[env_name]())

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # ─── Google service account (optional) ────────────────────────
    raw_key = app.config["GOOGLE_SVC_KEY"]
    creds = None
    if raw_key:
        try:
            key_data = (
                json.loads(Path(raw_key).read_text())
                if Path(raw_key).is_file()
                else json.loads(raw_key)
            )
            creds = service_account.Credentials.from_service_account_info(
                key_data,
                scopes=[
                    "https://www.googleapis.com/auth/drive",
                    "https://www.googleapis.com/auth/spreadsheets",
                ],
            )
        except Exception as exc:  # pragma: no cover
            logging.getLogger(__name__).warning(
                "GOOGLE_SVC_KEY invalid or missing; Drive integration disabled (%s)", exc
            )
    app.config["GOOGLE_SVC_CREDS"] = creds

    # ─── SQLite FK enforcement (dev only) ─────────────────────────
    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):

        @event.listens_for(Engine, "connect")
        def _fk_pragma(conn, _):  # noqa: ANN001
            conn.execute("PRAGMA foreign_keys=ON")

    # ─── extensions ───────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    init_celery(app)
    init_oauth(app)

    # ─── blueprints ───────────────────────────────────────────────
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(organisation_bp, url_prefix="/api/organisation")
    app.register_blueprint(woot_bp, url_prefix="/api/woot")

    return app
