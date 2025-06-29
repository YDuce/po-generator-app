"""Main application factory."""

import os

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager

from app.api import catalog_bp, export_bp, webhook_bp
from app.api.auth import bp as auth_bp
from app.channels.woot.routes import bp as woot_bp
from app.extensions import db

login_manager = LoginManager()


def create_app(config_object: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    if config_object == "testing":
        app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    elif config_object:
        app.config.from_object(config_object)
    else:
        app.config.update(
            SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///app.db"),
        )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(woot_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
