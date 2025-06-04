import os
import datetime
from flask import request, jsonify, redirect, session, url_for
from api import api_bp as bp
from models import User, OAuthToken
from database import SessionLocal
from passlib.hash import bcrypt
import jwt

JWT_SECRET = os.getenv('JWT_SECRET', 'devsecret')
JWT_ALGO = 'HS256'
ACCESS_EXPIRES = 900  # 15 min
REFRESH_EXPIRES = 604800  # 7 days
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

# --- Password login ---
@bp.route('/auth/token', methods=['POST'])
def password_login():
    data = request.json or {}
    email = data.get('email')
    password = data.get('password')
    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()
    if not user or not bcrypt.verify(password, user.password_hash):
        return jsonify({'error': 'invalid credentials'}), 401
    access_token = jwt.encode({'sub': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=ACCESS_EXPIRES)}, JWT_SECRET, algorithm=JWT_ALGO)
    refresh_token = jwt.encode({'sub': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=REFRESH_EXPIRES)}, JWT_SECRET, algorithm=JWT_ALGO)
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token})

# --- Refresh token ---
@bp.route('/auth/refresh', methods=['POST'])
def refresh_token():
    data = request.json or {}
    token = data.get('refresh_token')
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        user_id = payload['sub']
    except Exception:
        return jsonify({'error': 'invalid token'}), 401
    access_token = jwt.encode({'sub': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=ACCESS_EXPIRES)}, JWT_SECRET, algorithm=JWT_ALGO)
    refresh_token = jwt.encode({'sub': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=REFRESH_EXPIRES)}, JWT_SECRET, algorithm=JWT_ALGO)
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token})

# --- Google OAuth2 login (stub) ---
@bp.route('/auth/google/login', methods=['GET'])
def google_login():
    # Redirect to Google OAuth consent (stub: just return a message)
    return jsonify({'message': f'Google OAuth login not implemented. Client ID: {GOOGLE_CLIENT_ID}'}), 501

@bp.route('/auth/google/callback', methods=['GET'])
def google_callback():
    # Exchange code for tokens, store in oauth_token, issue JWT (stub)
    return jsonify({'message': 'Google OAuth callback not implemented in this stub.'}), 501 