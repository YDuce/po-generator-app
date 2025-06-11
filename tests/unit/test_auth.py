"""Unit tests for authentication and session management."""

import pytest
from datetime import datetime, timedelta
import jwt
from flask import current_app

from app.core.auth.service import AuthService
from app.core.auth.models import User
from app.core.auth.models import Session

def test_create_session(auth_client, db_session):
    """Test session creation."""
    # Get user from auth_client fixture
    user = db_session.query(User).filter_by(email="test@example.com").first()
    
    # Create auth service
    service = AuthService(db_session, current_app.config["SECRET_KEY"])
    
    # Create session
    session_info = service.create_session(user)
    
    # Verify session info
    assert "token" in session_info
    assert "expires_at" in session_info
    assert "user" in session_info
    assert session_info["user"]["email"] == user.email
    
    # Verify session in database
    session = db_session.query(Session).filter_by(token=session_info["token"]).first()
    assert session is not None
    assert session.user_id == user.id
    assert session.expires_at > datetime.utcnow()

def test_validate_session(auth_client, db_session):
    """Test session validation."""
    # Get user from auth_client fixture
    user = db_session.query(User).filter_by(email="test@example.com").first()
    
    # Create auth service
    service = AuthService(db_session, current_app.config["SECRET_KEY"])
    
    # Create session
    session_info = service.create_session(user)
    
    # Validate session
    validated_user = service.validate_session(session_info["token"])
    assert validated_user is not None
    assert validated_user.email == user.email
    
    # Verify last activity was updated
    session = db_session.query(Session).filter_by(token=session_info["token"]).first()
    assert session.last_activity > datetime.utcnow() - timedelta(seconds=5)

def test_validate_expired_session(auth_client, db_session):
    """Test validation of expired session."""
    # Get user from auth_client fixture
    user = db_session.query(User).filter_by(email="test@example.com").first()
    
    # Create auth service
    service = AuthService(db_session, current_app.config["SECRET_KEY"])
    
    # Create session with short expiration
    session_info = service.create_session(user, expires_in=1)
    
    # Wait for session to expire
    import time
    time.sleep(2)
    
    # Try to validate expired session
    validated_user = service.validate_session(session_info["token"])
    assert validated_user is None
    
    # Verify session was removed
    session = db_session.query(Session).filter_by(token=session_info["token"]).first()
    assert session is None

def test_revoke_session(auth_client, db_session):
    """Test session revocation."""
    # Get user from auth_client fixture
    user = db_session.query(User).filter_by(email="test@example.com").first()
    
    # Create auth service
    service = AuthService(db_session, current_app.config["SECRET_KEY"])
    
    # Create session
    session_info = service.create_session(user)
    
    # Revoke session
    result = service.revoke_session(session_info["token"])
    assert result is True
    
    # Verify session was removed
    session = db_session.query(Session).filter_by(token=session_info["token"]).first()
    assert session is None
    
    # Try to validate revoked session
    validated_user = service.validate_session(session_info["token"])
    assert validated_user is None

def test_cleanup_expired_sessions(auth_client, db_session):
    """Test cleanup of expired sessions."""
    # Get user from auth_client fixture
    user = db_session.query(User).filter_by(email="test@example.com").first()
    
    # Create auth service
    service = AuthService(db_session, current_app.config["SECRET_KEY"])
    
    # Create multiple sessions
    sessions = []
    for _ in range(3):
        session_info = service.create_session(user, expires_in=1)
        sessions.append(session_info)
    
    # Wait for sessions to expire
    import time
    time.sleep(2)
    
    # Clean up expired sessions
    count = service.cleanup_expired_sessions()
    assert count == 3
    
    # Verify all sessions were removed
    for session_info in sessions:
        session = db_session.query(Session).filter_by(token=session_info["token"]).first()
        assert session is None

def test_jwt_token_validation(auth_client, db_session):
    """Test JWT token validation."""
    # Get user from auth_client fixture
    user = db_session.query(User).filter_by(email="test@example.com").first()
    
    # Create auth service
    service = AuthService(db_session, current_app.config["SECRET_KEY"])
    
    # Create session
    session_info = service.create_session(user)
    
    # Decode and verify JWT token
    payload = jwt.decode(
        session_info["token"],
        current_app.config["SECRET_KEY"],
        algorithms=["HS256"]
    )
    
    assert payload["sub"] == user.id
    assert payload["email"] == user.email
    assert "exp" in payload
    assert "iat" in payload

def test_upsert_user(auth_client, db_session):
    """Test user upsert functionality."""
    # Test data
    user_info = {
        "email": "new@example.com",
        "given_name": "New",
        "family_name": "User",
        "name": "New User"
    }
    
    # Create user
    from app.core.auth.service import upsert_user
    user = upsert_user(db_session, user_info)
    
    # Verify user was created
    assert user.email == user_info["email"]
    assert user.first_name == user_info["given_name"]
    assert user.last_name == user_info["family_name"]
    
    # Update user info
    updated_info = {
        "email": user_info["email"],
        "given_name": "Updated",
        "family_name": "Name"
    }
    
    # Upsert user
    updated_user = upsert_user(db_session, updated_info)
    
    # Verify user was updated
    assert updated_user.email == user_info["email"]
    assert updated_user.first_name == updated_info["given_name"]
    assert updated_user.last_name == updated_info["family_name"] 