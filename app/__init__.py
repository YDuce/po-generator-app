from __future__ import annotations

import json, logging, os
from flask import Flask
from google.oauth2 import service_account
from dotenv import load_dotenv

from .extensions   import db, migrate, cors
from .config       import config
from .core.oauth   import init_oauth
from .api.health   import bp as health_bp
from .api.auth     import bp as auth_bp
from .api.organisation import bp as organisation_bp
from channels.woot.routes import bp as woot_bp

load_dotenv()
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

def create_app(env: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    env_name = env or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config[env_name])
    logging.info("Starting app in %s mode", env_name)

    svc_key = os.getenv("GOOGLE_SVC_KEY")
    creds = None
    if svc_key:
        key_json = json.loads(svc_key)
        creds = service_account.Credentials.from_service_account_info(
            key_json,
            scopes=[
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
            ],
        )
    app.config["GOOGLE_SVC_CREDS"] = creds

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    init_oauth(app)

    app.register_blueprint(health_bp,        url_prefix="/health")
    app.register_blueprint(auth_bp,          url_prefix="/api/auth")
    app.register_blueprint(organisation_bp,  url_prefix="/api/organisation")
    app.register_blueprint(woot_bp,         url_prefix="/api/woot")

    with app.app_context():
        pass
    return app
