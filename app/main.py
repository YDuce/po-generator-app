"""Main application factory."""

import logging
import os
from flask import Flask, send_from_directory, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_dance.contrib.google import make_google_blueprint
from .core.models.base import Base
from app.api import catalog_bp, export_bp
from app.api.auth import bp as auth_bp
# from app.channels.woot.routes import bp as woot_bp
from app.core.oauth import init_oauth

logger = logging.getLogger(__name__)

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    """Load user from database."""
    from app.models.user import User
    return User.query.get(int(user_id))

def create_app(config_object=None):
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='../frontend/dist')
    
    # Load configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object('app.config.Config')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app, supports_credentials=True, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Initialize OAuth
    init_oauth(app)
    
    # Register blueprints with /api prefix
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(catalog_bp, url_prefix='/api/catalog')
    app.register_blueprint(export_bp, url_prefix='/api/export')
#     app.register_blueprint(woot_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Serve static files
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)

    # Serve index.html for all routes except API routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path.startswith('api/'):
            return jsonify({'error': 'Not Found'}), 404
        return send_from_directory(app.static_folder, 'index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000) 