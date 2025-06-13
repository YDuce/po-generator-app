# import pytest
# from unittest.mock import patch, MagicMock
# from app.core import oauth
# from app.core.auth.models import User
# from app import db
# from app.core.auth.models import Session
# from app.core.auth.service import AuthService
#
# def test_oauth_flow(client, db_session) -> None:
#     """Test the complete OAuth flow including user creation and session management."""
#     # Mock Google OAuth response
#     mock_oauth_response = {
#         'id': '123456789',
#         'email': 'test@example.com',
#         'name': 'Test User',
#         'picture': 'https://example.com/photo.jpg'
#     }
#
#     with patch('app.core.oauth.google.session.get') as mock_get:
#         mock_get.return_value.ok = True
#         mock_get.return_value.json.return_value = mock_oauth_response
#
#         # Simulate OAuth callback
#         response = client.get('/auth/callback/google')
#         assert response.status_code == 302  # Redirect after successful auth
#
#         # Verify user was created in database
#         user = db_session.query(User).filter_by(email=mock_oauth_response['email']).first()
#         assert user is not None
#         assert user.google_id == mock_oauth_response['id']
#         assert user.name == mock_oauth_response['name']
#
#         # Verify session was created
#         with client.session_transaction() as session:
#             assert 'user_id' in session
#             assert session['user_id'] == user.id
#
# def test_oauth_error_handling(client) -> None:
#     """Test OAuth error scenarios."""
#     # Test invalid state
#     response = client.get('/auth/callback/google?error=invalid_state')
#     assert response.status_code == 400
#
#     # Test access denied
#     response = client.get('/auth/callback/google?error=access_denied')
#     assert response.status_code == 403
#
# def test_protected_routes(client, db_session) -> None:
#     """Test that protected routes require authentication."""
#     # Try accessing protected route without auth
#     response = client.get('/api/workspace')
#     assert response.status_code == 401
#
#     # Create test user
#     user = User(
#         email='test@example.com',
#         name='Test User',
#         google_id='123456789'
#     )
#     db_session.add(user)
#     db_session.commit()
#
#     # Login user
#     with client.session_transaction() as session:
#         session['user_id'] = user.id
#
#     # Now try accessing protected route
#     response = client.get('/api/workspace')
#     assert response.status_code == 200
#
# def test_protected_route_requires_auth(client) -> None:
#     """Test that protected routes require authentication."""
#     # Try accessing protected route without auth
#     response = client.get('/api/woot/workspace')
#     assert response.status_code == 401
#
# def test_protected_route_with_auth(client, db_session) -> None:
#     """Test accessing protected route with authentication."""
#     # Create test user
#     user = User(
#         email='test@example.com',
#         name='Test User',
#         google_id='123456789'
#     )
#     db_session.add(user)
#     db_session.commit()
#
#     # Login user
#     with client.session_transaction() as session:
#         session['user_id'] = user.id
#
#     # Access protected route
#     response = client.get('/api/woot/workspace')
#     assert response.status_code == 404  # Workspace not found, but auth passed
#
# def test_auth_middleware_invalid_session(client) -> None:
#     """Test auth middleware with invalid session."""
#     # Set invalid user ID in session
#     with client.session_transaction() as session:
#         session['user_id'] = 999999  # Non-existent user ID
#
#     # Try accessing protected route
#     response = client.get('/api/woot/workspace')
#     assert response.status_code == 401
#
# def test_auth_middleware_no_session(client) -> None:
#     """Test auth middleware with no session."""
#     # Try accessing protected route without session
#     response = client.get('/api/woot/workspace')
#     assert response.status_code == 401
#
# def test_auth_middleware_session_expired(client, db_session) -> None:
#     """Test auth middleware with expired session."""
#     # Create test user
#     user = User(
#         email='test@example.com',
#         name='Test User',
#         google_id='123456789'
#     )
#     db_session.add(user)
#     db_session.commit()
#
#     # Set user ID in session
#     with client.session_transaction() as session:
#         session['user_id'] = user.id
#
#     # Delete user to simulate expired session
#     db_session.delete(user)
#     db_session.commit()
#
#     # Try accessing protected route
#     response = client.get('/api/woot/workspace')
#     assert response.status_code == 401
#
# def test_google_oauth_callback(client, db_session) -> None:
#     """Test Google OAuth callback."""
#     # Mock Google OAuth response
#     mock_user_info = {
#         "email": "test@example.com",
#         "given_name": "Test",
#         "family_name": "User"
#     }
#
#     with patch('flask_dance.contrib.google.google.authorized', True), \
#          patch('flask_dance.contrib.google.google.get') as mock_get:
#
#         # Mock successful user info response
#         mock_get.return_value.ok = True
#         mock_get.return_value.json.return_value = mock_user_info
#
#         # Call OAuth callback
#         response = client.get('/auth/google/authorized')
#         assert response.status_code == 302  # Redirect to dashboard
#
#         # Verify user was created
#         user = User.query.filter_by(email='test@example.com').first()
#         assert user is not None
#         assert user.first_name == 'Test'
#         assert user.last_name == 'User'
#
#         # Verify session was created
#         with client.session_transaction() as session:
#             assert 'token' in session
#             token = session['token']
#
#         # Verify session in database
#         db_session = Session.query.filter_by(token=token).first()
#         assert db_session is not None
#         assert db_session.user_id == user.id
#
# def test_google_oauth_callback_no_token(client, db_session) -> None:
#     """Test Google OAuth callback without token."""
#     with patch('flask_dance.contrib.google.google.authorized', False):
#         # Call OAuth callback
#         response = client.get('/auth/google/authorized')
#         assert response.status_code == 302  # Redirect to login
#
#         # Verify no user was created
#         user = User.query.filter_by(email='test@example.com').first()
#         assert user is None
#
#         # Verify session was not set
#         with client.session_transaction() as session:
#             assert 'token' not in session
#
# def test_logout(auth_client, db_session) -> None:
#     """Test user logout."""
#     # Get current session token
#     with auth_client.session_transaction() as session:
#         token = session.get('token')
#         assert token is not None
#
#     # Call logout
#     response = auth_client.get('/api/auth/logout')
#     assert response.status_code == 200
#     assert response.json['message'] == 'Logged out successfully'
#
#     # Verify session was removed
#     with auth_client.session_transaction() as session:
#         assert 'token' not in session
#
#     # Verify session was revoked in database
#     session = Session.query.filter_by(token=token).first()
#     assert session is None
#
# def test_get_current_user(auth_client) -> None:
#     """Test getting current user info."""
#     response = auth_client.get('/api/auth/me')
#     assert response.status_code == 200
#
#     data = response.json
#     assert data['email'] == 'test@example.com'
#     assert data['first_name'] == 'Test'
#     assert data['last_name'] == 'User'
#
# def test_session_validation(auth_client, db_session) -> None:
#     """Test session validation."""
#     # Get current session token
#     with auth_client.session_transaction() as session:
#         token = session.get('token')
#         assert token is not None
#
#     # Create auth service
#     auth_service = AuthService(db_session, 'test-secret-key')
#
#     # Validate session
#     user = auth_service.validate_session(token)
#     assert user is not None
#     assert user.email == 'test@example.com'
#
#     # Verify last activity was updated
#     session = Session.query.filter_by(token=token).first()
#     assert session.last_activity is not None
#
# def test_session_expiration(auth_client, db_session) -> None:
#     """Test session expiration."""
#     # Get current session token
#     with auth_client.session_transaction() as session:
#         token = session.get('token')
#         assert token is not None
#
#     # Create auth service
#     auth_service = AuthService(db_session, 'test-secret-key')
#
#     # Expire session
#     session = Session.query.filter_by(token=token).first()
#     session.expires_at = session.expires_at.replace(year=2000)  # Set to past
#     db_session.commit()
#
#     # Try to validate expired session
#     user = auth_service.validate_session(token)
#     assert user is None
#
#     # Verify session was removed
#     session = Session.query.filter_by(token=token).first()
#     assert session is None