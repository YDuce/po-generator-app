"""Flask application factory."""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

logger = logging.getLogger(__name__)


def create_app(test_config=None):
    """Create and configure the Flask application.
    
    Args:
        test_config: Optional test configuration
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    if test_config is None:
        app.config.from_object("app.config.Config")
    elif isinstance(test_config, dict):
        app.config.update(test_config)
    else:
        app.config.from_object(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from app.api import catalog_bp, export_bp
    from app.api.auth import bp as auth_bp
    from app.channels.woot.routes import bp as woot_bp
    from app.core.oauth import init_oauth

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(woot_bp)

    # Initialize OAuth
    init_oauth(app)

    # with app.app_context():
    #     from app.core.models.base import Base
    #     Base.metadata.create_all(db.engine)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Application initialized")

    return app 