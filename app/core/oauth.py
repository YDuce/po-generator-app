"""OAuth configuration and services.

Layer: core
"""

import logging
from flask import current_app
from flask_dance.contrib.google import make_google_blueprint

logger = logging.getLogger(__name__)

def create_google_blueprint():
    """Create and configure the Google OAuth blueprint.
    
    Returns:
        Blueprint: Configured Google OAuth blueprint
    """
    return make_google_blueprint(
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        scope=["profile", "email"],
        redirect_to="auth.google_callback"
    )

def init_oauth(app):
    """Initialize OAuth configuration.
    
    Args:
        app: Flask application instance
    """
    with app.app_context():
        google_bp = create_google_blueprint()
        app.register_blueprint(google_bp, url_prefix="/login/google")
        return google_bp 