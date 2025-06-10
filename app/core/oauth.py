"""OAuth configuration and services.

Layer: core
"""

import logging
from flask import current_app, Blueprint
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_user
from app.core.models.user import User
from app import db
from .models import OAuth

logger = logging.getLogger(__name__)

def create_google_bp() -> Blueprint:
    """Create and configure the Google OAuth blueprint for /api/auth/google/authorized."""
    scopes = [
        "profile",
        "email",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    google_bp = make_google_blueprint(
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        scope=scopes,
        redirect_url="/api/auth/google/authorized",
        storage=SQLAlchemyStorage(OAuth, db.session, user=current_user, user_required=False)
    )
    return google_bp

def init_oauth(app) -> None:
    """Initialize OAuth configuration for /api/auth/google/authorized."""
    with app.app_context():
        if not app.config.get("GOOGLE_CLIENT_ID"):
            raise ValueError("GOOGLE_CLIENT_ID is required")
        if not app.config.get("GOOGLE_CLIENT_SECRET"):
            raise ValueError("GOOGLE_CLIENT_SECRET is required")
        google_bp = create_google_bp()
        app.register_blueprint(google_bp, url_prefix="/api/auth")
        
        @oauth_authorized.connect_via(google_bp)
        def google_logged_in(blueprint, token):
            """Handle successful OAuth login."""
            if not token:
                logger.error("Failed to get OAuth token")
                return False
                
            try:
                resp = google.get("/oauth2/v2/userinfo")
                if not resp.ok:
                    logger.error("Failed to fetch user info: %s", resp.text)
                    return False
                    
                info = resp.json()
                user = User.query.filter_by(email=info['email']).first()
                
                if not user:
                    user = User(
                        email=info['email'],
                        first_name=info.get('given_name', ''),
                        last_name=info.get('family_name', ''),
                        google_id=info['id']
                    )
                    db.session.add(user)
                    db.session.commit()
                
                # Store OAuth token
                oauth = OAuth(
                    user_id=user.id,
                    provider='google',
                    token=token
                )
                db.session.add(oauth)
                db.session.commit()
                
                # Log in the user
                login_user(user)
                
                return True
                
            except Exception as e:
                logger.error("OAuth login error: %s", str(e))
                return False 
