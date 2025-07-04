"""Flask application factory."""

from flask import Flask
from flask_migrate import Migrate

from .extensions import db

from .core.config.settings import settings
from .api.routes import auth_bp, organisation_bp, webhook_routes, reallocation_bp
from .channels import load_channels


migrate = Migrate()


def create_app() -> Flask:
    app = Flask(__name__)
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

    @app.route("/health")
    def root_health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    return app
