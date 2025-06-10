from typing import Optional, Any
from app.models import User, Session
from app.extensions import db

class AuthService:
    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return User.query.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return User.query.filter_by(email=email).first()

    def create_user(self, email: str, password: str, name: str) -> User:
        """Create a new user."""
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def update_user(self, user_id: int, data: dict[str, Any]) -> User:
        """Update a user."""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()
        return user

    def delete_user(self, user_id: int) -> None:
        """Delete a user."""
        user = self.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        db.session.delete(user)
        db.session.commit()

    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate a session."""
        session = Session.query.filter_by(session_id=session_id).first()
        if not session:
            return None
        return self.get_user(session.user_id)

    def create_session(self, user_id: int) -> str:
        """Create a new session."""
        session = Session(user_id=user_id)
        db.session.add(session)
        db.session.commit()
        return session.session_id

    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        session = Session.query.filter_by(session_id=session_id).first()
        if not session:
            raise ValueError(f"Session {session_id} not found")
        db.session.delete(session)
        db.session.commit() 