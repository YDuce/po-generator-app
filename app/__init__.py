"""Flask application factory.

Layer: app
"""
from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from flask import Flask

from .config import config
from .extensions import cors, db, migrate
from .api.auth import bp as auth_bp
from .api.health import bp as health_bp
from .core.oauth import init_oauth

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def create_app(env: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    env = env or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config.get(env, config["default"]))
    logging.info("Starting app in %s mode", env)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    init_oauth(app)

    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    with app.app_context():
        db.create_all()

    return app
