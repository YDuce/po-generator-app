"""Authentication API endpoints.

Layer: api
"""
import logging
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, session
from flask_dance.contrib.google import google
from flask_login import login_user, logout_user, login_required, current_user

from app.core import oauth
from app.services.auth import upsert_user
from app.core.auth.service import AuthService
from app import db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
logger = logging.getLogger(__name__)

def get_auth_service():
    """Get the auth service instance."""
    return AuthService(db.session, current_app.config["SECRET_KEY"])

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
    
    # Create session
    auth = get_auth_service()
    session_obj = auth.create_session(user)
    
    # Store token in session
    session['token'] = session_obj.token
    
    # Redirect to frontend with token
    return redirect(f"{current_app.config['FRONTEND_URL']}/dashboard?token={session_obj.token}")

@bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    if 'token' in session:
        auth = get_auth_service()
        auth.revoke_session(session['token'])
        session.pop('token', None)
    
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@bp.route("/me")
@login_required
def get_current_user():
    """Get current user info."""
    return jsonify({
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "company_name": current_user.company_name,
        "company_address": current_user.company_address,
        "phone": current_user.phone
    })

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