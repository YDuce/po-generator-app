from flask import Blueprint, request, jsonify, current_app, redirect, url_for
import jwt
from functools import wraps
from app.extensions import db
from app.core.auth.service import AuthService, create_jwt_for_user
from app.core.auth.models import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# JWT decorator
def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization','').replace('Bearer ','')
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
        except Exception:
            return jsonify({'error':'Unauthorized'}), 401
        return f(user, *args, **kwargs)
    return wrapper

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email'); pwd = data.get('password')
    if not email or not pwd:
        return jsonify({'error':'Email and password required'}),400
    svc = AuthService(db.session)
    user = svc.create_user(email,pwd)
    token = create_jwt_for_user(user)
    return jsonify({'token':token,'user':user.to_dict()}),201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email'); pwd = data.get('password')
    svc = AuthService(db.session)
    user = svc.authenticate(email,pwd)
    if not user:
        return jsonify({'error':'Invalid credentials'}),401
    token = create_jwt_for_user(user)
    return jsonify({'token':token,'user':user.to_dict()}),200

@bp.route('/refresh', methods=['POST'])
@token_required
def refresh(user):
    token = create_jwt_for_user(user)
    return jsonify({'token':token}),200

@bp.route('/me', methods=['GET'])
@token_required
def me(user):
    return jsonify(user.to_dict()),200
