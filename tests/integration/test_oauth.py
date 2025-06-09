"""Integration tests for OAuth functionality."""

import pytest
from unittest.mock import patch, MagicMock
from app.models.user import User

def test_google_oauth_callback(client, db_session):
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

def test_google_oauth_callback_existing_user(client, db_session):
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

def test_google_oauth_callback_error(client, db_session):
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

def test_google_oauth_callback_no_token(client, db_session):
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