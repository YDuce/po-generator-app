import pytest
from unittest.mock import patch, MagicMock
from app.core import oauth
from app.models.user import User
from app import db

def test_oauth_flow(client, db_session):
    """Test the complete OAuth flow including user creation and session management."""
    # Mock Google OAuth response
    mock_oauth_response = {
        'id': '123456789',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': 'https://example.com/photo.jpg'
    }
    
    with patch('app.core.oauth.google.session.get') as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_oauth_response
        
        # Simulate OAuth callback
        response = client.get('/auth/callback/google')
        assert response.status_code == 302  # Redirect after successful auth
        
        # Verify user was created in database
        user = db_session.query(User).filter_by(email=mock_oauth_response['email']).first()
        assert user is not None
        assert user.google_id == mock_oauth_response['id']
        assert user.name == mock_oauth_response['name']
        
        # Verify session was created
        with client.session_transaction() as session:
            assert 'user_id' in session
            assert session['user_id'] == user.id

def test_oauth_error_handling(client):
    """Test OAuth error scenarios."""
    # Test invalid state
    response = client.get('/auth/callback/google?error=invalid_state')
    assert response.status_code == 400
    
    # Test access denied
    response = client.get('/auth/callback/google?error=access_denied')
    assert response.status_code == 403

def test_protected_routes(client, db_session):
    """Test that protected routes require authentication."""
    # Try accessing protected route without auth
    response = client.get('/api/workspace')
    assert response.status_code == 401
    
    # Create test user
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Now try accessing protected route
    response = client.get('/api/workspace')
    assert response.status_code == 200 

def test_protected_route_requires_auth(client):
    """Test that protected routes require authentication."""
    # Try accessing protected route without auth
    response = client.get('/api/woot/workspace')
    assert response.status_code == 401

def test_protected_route_with_auth(client, db_session):
    """Test accessing protected route with authentication."""
    # Create test user
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Access protected route
    response = client.get('/api/woot/workspace')
    assert response.status_code == 404  # Workspace not found, but auth passed

def test_auth_middleware_invalid_session(client):
    """Test auth middleware with invalid session."""
    # Set invalid user ID in session
    with client.session_transaction() as session:
        session['user_id'] = 999999  # Non-existent user ID
    
    # Try accessing protected route
    response = client.get('/api/woot/workspace')
    assert response.status_code == 401

def test_auth_middleware_no_session(client):
    """Test auth middleware with no session."""
    # Try accessing protected route without session
    response = client.get('/api/woot/workspace')
    assert response.status_code == 401

def test_auth_middleware_session_expired(client, db_session):
    """Test auth middleware with expired session."""
    # Create test user
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Set user ID in session
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Delete user to simulate expired session
    db_session.delete(user)
    db_session.commit()
    
    # Try accessing protected route
    response = client.get('/api/woot/workspace')
    assert response.status_code == 401 