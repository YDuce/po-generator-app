"""Flask application factory."""

from flask import Flask

from .logging import configure_logging
from flask_migrate import Migrate

from .extensions import db
from .core.config.settings import get_settings
from .api.routes import (
    auth_bp,
    organisation_bp,
    webhook_routes,
    reallocation_bp,
    health_bp,
)
from .channels import load_channels

migrate = Migrate()


def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)
    settings = get_settings()
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SECRET_KEY"] = settings.secret_key
    db.init_app(app)
    migrate.init_app(app, db)

    # Load channel plug-ins
    app.extensions["channels"] = load_channels()

    app.register_blueprint(auth_bp)
    app.register_blueprint(organisation_bp)
    app.register_blueprint(reallocation_bp)
    for bp in webhook_routes:
        app.register_blueprint(bp)

    app.register_blueprint(health_bp)

    return app


__all__ = ["create_app", "db"]
