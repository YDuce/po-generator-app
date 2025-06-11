import jwt
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app.core.auth.models import User

# JWT helper
def create_jwt_for_user(user):
    now = datetime.utcnow()
    exp = now + current_app.config['JWT_EXPIRATION']
    payload = {'user_id': user.id, 'iat': now, 'exp': exp}
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

# OAuth upsert
def upsert_user(db_session, info):
    user = db_session.query(User).filter_by(email=info['email']).first()
    if not user:
        user = User(email=info['email'],
                    first_name=info.get('given_name'),
                    last_name=info.get('family_name'),
                    google_id=info.get('id'))
        db_session.add(user)
    else:
        user.first_name = info.get('given_name', user.first_name)
        user.last_name  = info.get('family_name', user.last_name)
    db_session.commit()
    return user

class AuthService:
    def __init__(self, db_session):
        self.db = db_session
    def create_user(self,email,password):
        hashed=generate_password_hash(password)
        u=User(email=email,password_hash=hashed)
        self.db.add(u); self.db.commit(); return u
    def authenticate(self,email,password):
        u=self.db.query(User).filter_by(email=email).first()
        return u if u and u.password_hash and check_password_hash(u.password_hash,password) else None
