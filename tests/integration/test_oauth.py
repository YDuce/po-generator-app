"""Integration tests for OAuth functionality."""

import pytest
from unittest.mock import patch, MagicMock
from app.core.auth.models import User
from flask import url_for

def test_google_oauth_callback(client, db_session) -> None:
    """Test Google OAuth callback flow."""
    # Mock Google OAuth response
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.json.return_value = {
        'id': '123456789',
        'email': 'test@example.com',
        'name': 'Test User'
    }
    
    with patch('flask_dance.contrib.google.google.authorized', True), \
         patch('flask_dance.contrib.google.google.get', return_value=mock_resp):
        
        # Call OAuth callback
        response = client.get('/auth/google/authorized')
        assert response.status_code == 200
        
        # Verify user was created
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.google_id == '123456789'
        assert user.name == 'Test User'
        
        # Verify session was set
        with client.session_transaction() as session:
            assert session['user_id'] == user.id

def test_google_oauth_callback_existing_user(client, db_session) -> None:
    """Test Google OAuth callback with existing user."""
    # Create existing user
    user = User(
        email='test@example.com',
        name='Existing User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Mock Google OAuth response
    mock_resp = MagicMock()
    mock_resp.ok = True
    mock_resp.json.return_value = {
        'id': '123456789',
        'email': 'test@example.com',
        'name': 'Updated Name'
    }
    
    with patch('flask_dance.contrib.google.google.authorized', True), \
         patch('flask_dance.contrib.google.google.get', return_value=mock_resp):
        
        # Call OAuth callback
        response = client.get('/auth/google/authorized')
        assert response.status_code == 200
        
        # Verify user was updated
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.name == 'Updated Name'
        
        # Verify session was set
        with client.session_transaction() as session:
            assert session['user_id'] == user.id

def test_google_oauth_callback_error(client, db_session) -> None:
    """Test Google OAuth callback error handling."""
    # Mock Google OAuth error
    mock_resp = MagicMock()
    mock_resp.ok = False
    mock_resp.text = 'Error fetching user info'
    
    with patch('flask_dance.contrib.google.google.authorized', True), \
         patch('flask_dance.contrib.google.google.get', return_value=mock_resp):
        
        # Call OAuth callback
        response = client.get('/auth/google/authorized')
        assert response.status_code == 302  # Redirect to login
        
        # Verify no user was created
        user = User.query.filter_by(email='test@example.com').first()
        assert user is None
        
        # Verify session was not set
        with client.session_transaction() as session:
            assert 'user_id' not in session

def test_google_oauth_callback_no_token(client, db_session) -> None:
    """Test Google OAuth callback without token."""
    with patch('flask_dance.contrib.google.google.authorized', False):
        # Call OAuth callback
        response = client.get('/auth/google/authorized')
        assert response.status_code == 302  # Redirect to login
        
        # Verify no user was created
        user = User.query.filter_by(email='test@example.com').first()
        assert user is None
        
        # Verify session was not set
        with client.session_transaction() as session:
            assert 'user_id' not in session

def test_google_login_redirect(client) -> None:
    """Test Google login redirect."""
    response = client.get("/api/auth/google")
    assert response.status_code == 302
    assert "accounts.google.com" in response.location

def test_google_callback_success(client, db_session, mock_oauth_responses) -> None:
    """Test successful Google OAuth callback."""
    # Mock Google OAuth response
    with patch("flask_dance.contrib.google.google") as mock_google:
        mock_google.authorized = True
        mock_google.get.return_value.ok = True
        mock_google.get.return_value.json.return_value = mock_oauth_responses["user_info"]
        
        # Call callback endpoint
        response = client.get("/api/auth/google/callback")
        
        # Verify redirect to frontend
        assert response.status_code == 302
        assert "dashboard" in response.location
        assert "token=" in response.location
        
        # Verify user was created
        from app.core.auth.models import User
        user = User.query.filter_by(email=mock_oauth_responses["user_info"]["email"]).first()
        assert user is not None
        assert user.first_name == mock_oauth_responses["user_info"]["given_name"]
        assert user.last_name == mock_oauth_responses["user_info"]["family_name"]

def test_google_callback_unauthorized(client) -> None:
    """Test Google OAuth callback when not authorized."""
    # Mock unauthorized state
    with patch("flask_dance.contrib.google.google") as mock_google:
        mock_google.authorized = False
        
        # Call callback endpoint
        response = client.get("/api/auth/google/callback")
        
        # Verify redirect to login
        assert response.status_code == 302
        assert "login" in response.location

def test_google_callback_error(client, db_session) -> None:
    """Test Google OAuth callback with error."""
    # Mock Google OAuth error
    with patch("flask_dance.contrib.google.google") as mock_google:
        mock_google.authorized = True
        mock_google.get.return_value.ok = False
        mock_google.get.return_value.text = "Error message"
        
        # Call callback endpoint
        response = client.get("/api/auth/google/callback")
        
        # Verify redirect to error page
        assert response.status_code == 302
        assert "login-error" in response.location

def test_token_refresh(auth_client) -> None:
    """Test JWT token refresh."""
    # Get current token from auth_client
    token = auth_client.environ_base["HTTP_AUTHORIZATION"].split(" ")[1]
    
    # Call refresh endpoint
    response = auth_client.post("/api/auth/refresh")
    
    # Verify new token
    assert response.status_code == 200
    assert "token" in response.json
    assert response.json["token"] != token

def test_protected_endpoint_with_token(auth_client) -> None:
    """Test accessing protected endpoint with valid token."""
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 200
    assert "email" in response.json
    assert response.json["email"] == "test@example.com"

def test_protected_endpoint_without_token(client) -> None:
    """Test accessing protected endpoint without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "error" in response.json
    assert "Token is missing" in response.json["error"]

def test_protected_endpoint_with_invalid_token(client) -> None:
    """Test accessing protected endpoint with invalid token."""
    client.environ_base["HTTP_AUTHORIZATION"] = "Bearer invalid_token"
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "error" in response.json
    assert "Invalid token" in response.json["error"]

def test_logout(auth_client) -> None:
    """Test user logout."""
    response = auth_client.get("/api/auth/logout")
    assert response.status_code == 200
    assert "message" in response.json
    assert "Logged out successfully" in response.json["message"]
    
    # Verify token is invalidated
    response = auth_client.get("/api/auth/me")
    assert response.status_code == 401 