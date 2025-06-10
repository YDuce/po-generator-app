"""Authentication API endpoints.

Layer: api
"""
import logging
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session, Response, render_template
from flask_dance.contrib.google import google
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.exceptions import Unauthorized

from app.core import oauth
from app.core.auth.service import upsert_user
from app.core.auth.service import AuthService
from app import db
from app.core.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
logger = logging.getLogger(__name__)

def get_auth_service() -> AuthService:
    """Get the auth service instance."""
    return AuthService(db.session, current_app.config["SECRET_KEY"])

def create_jwt_token(user, expires_delta=None) -> str:
    """Create a JWT token for the user.
    
    Args:
        user: User model instance
        expires_delta: Optional timedelta for token expiration
        
    Returns:
        str: JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=1)
        
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + expires_delta,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def token_required(f):
    """Decorator to require JWT token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@bp.route("/")
def landing() -> Response:
    """Serve the landing page."""
    return render_template('landing.html')

@bp.route("/google")
def google_login() -> Response:
    """Initiate Google OAuth login."""
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("auth.google_callback"))

@bp.route("/google/callback")
def google_callback() -> Response:
    """Handle Google OAuth callback and issue JWT token."""
    if not google.authorized:
        return redirect(url_for("google.login"))

    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            logger.error("Failed to fetch user info: %s", resp.text)
            return redirect(url_for("auth.login_error"))

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
        
        # Create JWT token
        token = create_jwt_token(user)
        
        # Redirect to frontend with token
        return redirect(f"{current_app.config['FRONTEND_URL']}/dashboard?token={token}")
        
    except Exception as e:
        logger.error("OAuth callback error: %s", str(e))
        return redirect(url_for("auth.login_error"))

@bp.route("/refresh", methods=["POST"])
@token_required
def refresh_token(current_user) -> Response:
    """Refresh the JWT token."""
    token = create_jwt_token(current_user)
    return jsonify({"token": token})

@bp.route("/logout")
@token_required
def logout(current_user) -> Response:
    """Clear the session token."""
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@bp.route("/me")
@token_required
def get_current_user(current_user) -> Response:
    """Get current user info."""
    return jsonify(current_user.to_dict())

@bp.route("/check", methods=["GET"])
@token_required
def check_auth(current_user) -> Response:
    """Check if user is authenticated."""
    return jsonify({
        "authenticated": True,
        "user": current_user.to_dict()
    })

@bp.route("/login-error")
def login_error() -> Response:
    """Handle login errors."""
    return jsonify({
        "error": "Authentication failed",
        "message": "There was an error during the authentication process"
    }), 401

@bp.route("/register", methods=["POST"])
def register() -> Response:
    """Register a new user."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    service = get_auth_service()
    try:
        user = service.create_user(email, password)
        token = service.create_token(user)
        return jsonify({"token": token, "user": user.to_dict()}), 201
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("registration failed: %s", exc)
        return jsonify({"error": str(exc)}), 400

@bp.route("/login", methods=["POST"])
def login() -> Response:
    """Login a user."""
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    service = get_auth_service()
    user = service.authenticate(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = service.create_token(user)
    return jsonify({"token": token, "user": user.to_dict()}) 