"""Authentication API endpoints.

Layer: api
"""
from flask import Blueprint, request, jsonify, current_app
from app.core.auth.service import AuthService
from app.extensions import db

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def get_auth_service() -> AuthService:
    """Get the auth service instance."""
    return AuthService(db.session, current_app.config['SECRET_KEY'])

@bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400
    
    service = get_auth_service()
    try:
        user = service.create_user(email, password)
        token = service.create_token(user)
        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/login', methods=['POST'])
def login():
    """Login a user."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'email and password are required'}), 400
    
    service = get_auth_service()
    user = service.authenticate(email, password)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = service.create_token(user)
    return jsonify({
        'token': token,
        'user': user.to_dict()
    })

@bp.route('/logout', methods=['POST'])
def logout():
    """Logout a user."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    service = get_auth_service()
    service.revoke_token(token)
    return jsonify({'message': 'Logged out successfully'})

@bp.route('/me', methods=['GET'])
def get_current_user():
    """Get the current user."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Invalid authorization header'}), 401
    
    token = auth_header.split(' ')[1]
    service = get_auth_service()
    user = service.verify_token(token)
    if not user:
        return jsonify({'error': 'Invalid token'}), 401
    
    return jsonify(user.to_dict()) 