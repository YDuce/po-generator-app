import jwt, logging
from functools import wraps
from typing import Callable
from flask import Blueprint, current_app, jsonify, request
from flask.typing import ResponseReturnValue
from app.extensions import db
from app.core.auth.service import AuthService, create_jwt_for_user
from app.core.models.user import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth"); log = logging.getLogger(__name__)


def token_required(f: Callable[[User], ResponseReturnValue]) -> Callable[..., ResponseReturnValue]:
    @wraps(f)
    def wrap(*a: object, **kw: object) -> ResponseReturnValue:
        tok = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(tok, current_app.config["JWT_SECRET"], algorithms=["HS256"])
            uid = int(payload["user_id"])
            user = User.query.get(uid)
        except Exception:
            return jsonify({"error": "unauthorized"}), 401
        return f(user, *a, **kw)
    return wrap


@bp.post("/register")
def register() -> ResponseReturnValue:
    d = request.get_json() or {}
    try:
        u = AuthService(db.session).create_user(d.get("email", ""), d.get("password", ""))
    except ValueError as e:
        return jsonify({"error": str(e)}), 409
    return jsonify({"token": create_jwt_for_user(u), "user": u.to_dict()}), 201


@bp.post("/login")
def login() -> ResponseReturnValue:
    d = request.get_json() or {}
    svc = AuthService(db.session)
    u = svc.authenticate(d.get("email", ""), d.get("password", ""))
    if not u:
        return jsonify({"error": "invalid"}), 401
    return jsonify({"token": create_jwt_for_user(u), "user": u.to_dict()}), 200


@bp.post("/refresh")
@token_required
def refresh(u: User) -> ResponseReturnValue:
    return jsonify({"token": create_jwt_for_user(u)}), 200


@bp.get("/me")
@token_required
def me(u: User) -> ResponseReturnValue:
    return jsonify(u.to_dict()), 200
