"""Flask application factory."""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_talisman import Talisman

from .api.routes import auth_bp, health_bp, organisation_bp, reallocation_bp, webhook_bp
from .channels import load_channels
from .core.config.settings import get_settings
from .extensions import db
from .logging import configure_logging

migrate = Migrate()


def create_app() -> Flask:
    configure_logging()
    app = Flask(__name__)
    settings = get_settings()
    CORS(app)
    Talisman(app, content_security_policy=None, force_https=False)
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.database_url
    app.config["SECRET_KEY"] = settings.secret_key
    db.init_app(app)
    migrate.init_app(app, db)

    # Load channel plug-ins
    app.extensions["channels"] = load_channels()

    app.register_blueprint(auth_bp)
    app.register_blueprint(organisation_bp)
    app.register_blueprint(reallocation_bp)
    app.register_blueprint(webhook_bp)

    app.register_blueprint(health_bp)

    return app


__all__ = ["create_app", "db"]
