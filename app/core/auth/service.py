from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from sqlalchemy.orm import Session
from app.core.models.user import User

def create_jwt_for_user(user: User) -> str:
    payload = {
        "user_id": user.id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + current_app.config.get("JWT_EXPIRATION", timedelta(days=1))
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")

def upsert_user(session: Session, info: dict) -> User:
    user = session.query(User).filter_by(email=info["email"]).first()
    if not user:
        user = User(
            email=info["email"],
            first_name=info.get("given_name"),
            last_name=info.get("family_name"),
            google_id=info.get("id"),
            organisation_id=1  # Ideally dynamic in future
        )
        session.add(user)
    else:
        user.first_name = info.get("given_name", user.first_name)
        user.last_name = info.get("family_name", user.last_name)
    session.commit()
    return user

class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, email: str, password: str) -> User:
        if self.session.query(User).filter_by(email=email).first():
            raise ValueError("Email already registered")
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            organisation_id=1  # This should later be dynamically assigned
        )
        self.session.add(user)
        self.session.commit()
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.session.query(User).filter_by(email=email).first()
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            return user
        return None
