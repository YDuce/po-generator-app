"""OAuth configuration and services.

Layer: core
"""

import logging
from flask import current_app, redirect, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound

from app.core.models.user import User
from app import db

logger = logging.getLogger(__name__)

# Stub for google_bp to satisfy import in tests/conftest.py
google_bp = None

def create_google_bp():
    """Create and configure the Google OAuth blueprint.
    
    Returns:
        tuple: (google, google_bp) - Google OAuth client and blueprint
    """
    # Configure OAuth scopes
    scopes = [
        "profile",  # Basic profile info
        "email",    # Email address
        "https://www.googleapis.com/auth/drive.file",  # Drive file access
        "https://www.googleapis.com/auth/spreadsheets"  # Sheets access
    ]
    
    # Create blueprint with storage
    google_bp = make_google_blueprint(
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        scope=scopes,
        redirect_to="auth.google_callback",
        storage=SQLAlchemyStorage(User, db.session, user=current_user)
    )
    
    # Set up OAuth error handling
    @oauth_error.connect_via(google_bp)
    def google_error(blueprint, message, response):
        """Handle OAuth errors."""
        logger.error("OAuth error: %s", message)
        return redirect(url_for("auth.login_error"))
    
    return google, google_bp

def init_oauth(app):
    """Initialize OAuth configuration.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        google, google_bp = create_google_bp()
        app.register_blueprint(google_bp, url_prefix="/login/google")
        return google_bp 