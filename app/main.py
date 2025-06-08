"""Main application factory."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from app.core.models.base import Base
from app.api import catalog_bp, export_bp
from app.api.auth import bp as auth_bp
from app.channels.woot.routes import bp as woot_bp

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_object=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object('app.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(woot_bp)
    
    # Create database tables
    with app.app_context():
        Base.metadata.create_all(db.engine)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) 