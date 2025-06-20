import jwt
import logging
from functools import wraps
from flask import Blueprint, current_app, jsonify, request
from app.extensions import db
from app.core.auth.service import AuthService, create_jwt_for_user
from app.core.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
log = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            user = db.session.get(User, payload["user_id"])
            if not user:
                raise ValueError("User not found")
        except Exception:
            return jsonify({"error": "unauthorized"}), 401
        return f(user, *args, **kwargs)
    return wrap

@bp.post("/register")
def register():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "email and password required"}), 400
    try:
        user = AuthService(db.session).create_user(email, password)
        token = create_jwt_for_user(user)
        return jsonify({"token": token, "user": user.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

@bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    user = AuthService(db.session).authenticate(email, password)
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    token = create_jwt_for_user(user)
    return jsonify({"token": token, "user": user.to_dict()}), 200

@bp.post("/refresh")
@token_required
def refresh(user: User):
    token = create_jwt_for_user(user)
    return jsonify({"token": token}), 200

@bp.get("/me")
@token_required
def me(user: User):
    return jsonify(user.to_dict()), 200
