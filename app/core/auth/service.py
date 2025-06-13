from __future__ import annotations
from datetime import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app.extensions import db
from app.core.models.user import User

def create_jwt_for_user(user: User) -> str:
    now = datetime.utcnow()
    exp = now + current_app.config["JWT_EXPIRATION"]
    return jwt.encode({"user_id": user.id, "exp": exp}, current_app.config["JWT_SECRET"], algorithm="HS256")

def upsert_user(session, info: dict) -> User:
    user = session.query(User).filter_by(email=info["email"]).first()
    if not user:
        user = User(email=info["email"], first_name=info.get("given_name"), last_name=info.get("family_name"), google_id=info.get("id"), organisation_id=1)
        session.add(user)
    else:
        user.first_name = info.get("given_name", user.first_name)
        user.last_name = info.get("family_name", user.last_name)
    session.commit()
    return user

class AuthService:
    def __init__(self, session):
        self.db = session

    def create_user(self, email: str, pw: str) -> User:
        if self.db.query(User).filter_by(email=email).first():
            raise ValueError("duplicate")
        u = User(email=email, password_hash=generate_password_hash(pw), organisation_id=1)
        self.db.add(u)
        self.db.commit()
        return u

    def authenticate(self, email: str, pw: str) -> User | None:
        u = self.db.query(User).filter_by(email=email).first()
        if not u or not u.password_hash or not check_password_hash(u.password_hash, pw):
            return None
        return u
