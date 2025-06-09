"""Authentication API endpoints.

Layer: api
"""
import logging
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import login_user, logout_user, login_required, current_user

from app.core import oauth
from app.services.auth import upsert_user
from app import db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
logger = logging.getLogger(__name__)

# Google OAuth blueprint
google_bp = make_google_blueprint(
    client_id=current_app.config.get("GOOGLE_CLIENT_ID"),
    client_secret=current_app.config.get("GOOGLE_CLIENT_SECRET"),
    scope=["profile", "email"],
    redirect_to="auth.google_callback"
)

def get_auth_service():
    """Get the auth service instance."""
    return oauth.AuthService(db.session, current_app.config["SECRET_KEY"])

@bp.route("/google")
def google_login():
    """Initiate Google OAuth login."""
    if not google.authorized:
        return redirect(url_for("google.login"))
    return redirect(url_for("auth.google_callback"))

@bp.route("/google/callback")
def google_callback():
    """Handle Google OAuth callback."""
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return jsonify({"error": "Failed to fetch user info"}), 400

    info = resp.json()
    user = upsert_user(db.session, info)
    login_user(user)
    
    # Create session token
    auth = get_auth_service()
    token = auth.create_token(user)
    
    # Store token in session
    session['token'] = token
    
    # Redirect to frontend with token
    return redirect(f"{current_app.config['FRONTEND_URL']}/dashboard?token={token}")

@bp.route("/me", methods=["GET"])
@login_required
def get_current_user():
    """Get the current user."""
    return jsonify(current_user.to_dict())

@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout the current user."""
    logout_user()
    session.clear()
    return jsonify({"message": "Logged out successfully"})

@bp.route("/check", methods=["GET"])
def check_auth():
    """Check if user is authenticated."""
    if current_user.is_authenticated:
        return jsonify({
            "authenticated": True,
            "user": current_user.to_dict()
        })
    return jsonify({"authenticated": False}), 401

@bp.route("/register", methods=["POST"])
def register():
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
def login():
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