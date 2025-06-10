"""
Flask application factory.

This module contains the application factory function that creates and configures
the Flask application. It initializes all extensions and registers blueprints.
"""

import os
import logging
from flask import Flask
from dotenv import load_dotenv
from .config import DevelopmentConfig, ProductionConfig
from .extensions import db, login, migrate, cors
from .api.health import bp as health_bp
from .api.auth import bp as auth_bp
from .core.oauth import init_oauth

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name=None):
    """Create Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    env = config_name or os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)
    logger.info("Environment: %s", env)

    # Log key config values
    logger.info("SECRET_KEY set: %s", 'Yes' if app.config.get('SECRET_KEY') else 'No')
    logger.info("DATABASE_URL: %s", app.config.get('DATABASE_URL'))
    logger.info("FRONTEND_URL: %s", app.config.get('FRONTEND_URL'))

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config.get('FRONTEND_URL') or '*'}})
    logger.info("Extensions initialized successfully")

    # Initialize OAuth (registers Google OAuth blueprint at /login/google)
    init_oauth(app)
    logger.info("OAuth initialized successfully")

    # Register blueprints
    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    logger.info("Blueprints registered successfully")

    # Ensure database tables exist
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

    return app