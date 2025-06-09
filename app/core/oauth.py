"""
OAuth logic for Google integration.
"""

import logging
from flask import current_app, session
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from sqlalchemy.orm.exc import NoResultFound
from app import db
from app.models.user import User

logger = logging.getLogger(__name__)

# Create the Google OAuth blueprint
google_bp = make_google_blueprint(
    client_id=None,  # Will be set from config
    client_secret=None,  # Will be set from config
    scope=["profile", "email", "https://www.googleapis.com/auth/drive.file"],
    storage=SQLAlchemyStorage(User, db.session, user=User.current_user),
)

google = google_bp  # ← expose for patching

__all__ = ["google_bp", "google"]

@oauth_authorized.connect_via(google_bp)
def google_logged_in(blueprint, token):
    """Handle successful Google OAuth login."""
    if not token:
        logger.warning("No token received from Google OAuth")
        return False

    try:
        resp = blueprint.session.get("/oauth2/v2/userinfo")
        if not resp.ok:
            logger.error("Failed to fetch userinfo from Google: %s", resp.text)
            return False

        google_info = resp.json()
        google_user_id = google_info["id"]

        # Find this OAuth token in the database, or create it
        query = User.query.filter_by(google_id=google_user_id)
        try:
            user = query.one()
            logger.info("Found existing user: %s", user.email)
        except NoResultFound:
            # Create a new user
            user = User(
                google_id=google_user_id,
                name=google_info["name"],
                email=google_info["email"],
            )
            db.session.add(user)
            db.session.commit()
            logger.info("Created new user: %s", user.email)

        # Store user ID in session
        session['user_id'] = user.id
        return True

    except Exception as e:
        logger.error("Error during Google OAuth login: %s", str(e))
        return False

def init_oauth(app):
    """Initialize OAuth configuration."""
    # Set OAuth credentials from config
    google_bp.client_id = app.config['GOOGLE_CLIENT_ID']
    google_bp.client_secret = app.config['GOOGLE_CLIENT_SECRET']
    
    # Register blueprint
    app.register_blueprint(google_bp, url_prefix="/auth") 