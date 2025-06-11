from __future__ import annotations
from flask import Flask
from dotenv import load_dotenv
import logging, os, json
from google.oauth2 import service_account

from .config import config
from .extensions import db, migrate, cors
from .api.auth import bp as auth_bp
from .api.health import bp as health_bp
from .api.organisation import bp as organisation_bp
from .core.oauth import init_oauth

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

def create_app(env: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    env = env or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config.get(env, config['default']))
    logging.info('Starting app in %s mode', env)

    # Load service account credentials
    key = json.loads(os.getenv('GOOGLE_SVC_KEY', '{}'))
    creds = service_account.Credentials.from_service_account_info(
        key,
        scopes=[
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets',
        ],
    )
    app.config['GOOGLE_SVC_CREDS'] = creds

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}})

    # Initialize OAuth blueprint
    init_oauth(app)

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix='/health')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(organisation_bp, url_prefix='/api/organisation')

    # Create tables
    with app.app_context():
        db.create_all()

    return app
