"""Flask application factory."""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

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
        app.config.from_object('app.config.Config')
    else:
        app.config.update(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints
    from app.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.channels.woot.routes import bp as woot_bp
    app.register_blueprint(woot_bp)
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    return app 