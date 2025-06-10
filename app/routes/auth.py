"""Authentication routes."""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.extensions import db
from app.core.oauth import google_bp

auth = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    login_user(user)
    return jsonify({
        'message': 'Logged in successfully',
        'user': user.to_dict()
    })

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth.route('/me')
@login_required
def me():
    """Get current user info."""
    return jsonify(current_user.to_dict())

@auth.route('/google/url')
def google_url():
    """Get Google OAuth URL."""
    return jsonify({
        'url': f"{current_app.config['FRONTEND_URL']}/auth/google"
    })

@auth.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback."""
    # TODO: Implement Google OAuth callback
    return jsonify({'message': 'Google OAuth callback'}) 