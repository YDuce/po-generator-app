# Authentication System

## Overview

The PO Generator App uses a combination of Google OAuth and JWT tokens for authentication. This document describes the authentication flow and implementation details.

## Authentication Flow

1. **Initial Login**
   - User clicks "Login with Google"
   - App redirects to Google OAuth consent screen
   - User grants permissions
   - Google redirects back to app with auth code

2. **Token Generation**
   - App exchanges auth code for access token
   - App fetches user info from Google
   - App creates/updates user in database
   - App generates JWT token
   - App redirects to frontend with token

3. **Session Management**
   - Frontend stores JWT token
   - Frontend includes token in API requests
   - Backend validates token on each request
   - Tokens expire after 1 hour
   - Frontend can refresh tokens

## Implementation Details

### OAuth Configuration

```python
# app/core/oauth.py
def create_google_bp():
    google_bp = make_google_blueprint(
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        scope=["profile", "email", "drive.file", "spreadsheets"],
        redirect_to="auth.google_callback"
    )
    return google, google_bp
```

### JWT Token Structure

```python
payload = {
    'sub': user.id,          # Subject (user ID)
    'email': user.email,     # User email
    'exp': expiration_time,  # Expiration time
    'iat': issued_at_time    # Issued at time
}
```

### Session Management

```python
# app/core/auth/service.py
class AuthService:
    def create_session(self, user: User, expires_in: int = 3600):
        token = self._create_jwt_token(user, expires_in)
        session = Session(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
        )
        return {
            'token': token,
            'expires_at': session.expires_at,
            'user': user.to_dict()
        }
```

## Security Considerations

1. **Token Security**
   - JWT tokens are signed with app secret key
   - Tokens expire after 1 hour
   - Tokens can be refreshed
   - Tokens are stored in HTTP-only cookies

2. **Session Security**
   - Sessions are stored in database
   - Sessions are cleaned up on expiration
   - Sessions can be revoked
   - Session activity is tracked

3. **OAuth Security**
   - OAuth tokens are stored securely
   - OAuth scopes are limited to required permissions
   - OAuth state is validated
   - OAuth errors are handled gracefully

## API Endpoints

### Authentication

```http
# Google OAuth Login
GET /api/auth/google

# OAuth Callback
GET /api/auth/google/callback

# Token Refresh
POST /api/auth/refresh
Authorization: Bearer <token>

# Logout
GET /api/auth/logout
Authorization: Bearer <token>
```

### User Management

```http
# Get Current User
GET /api/auth/me
Authorization: Bearer <token>

# Check Authentication
GET /api/auth/check
Authorization: Bearer <token>
```

## Error Handling

1. **OAuth Errors**
   - Invalid credentials
   - Scope rejection
   - Network errors
   - State mismatch

2. **Token Errors**
   - Expired token
   - Invalid signature
   - Missing token
   - Invalid format

3. **Session Errors**
   - Session not found
   - Session expired
   - Session revoked
   - Database errors

## Testing

The authentication system includes comprehensive tests:

1. **Unit Tests**
   - Token generation
   - Session management
   - User management
   - Error handling

2. **Integration Tests**
   - OAuth flow
   - API endpoints
   - Error responses
   - Session cleanup

## Configuration

Required environment variables:

```env
# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback/google

# JWT
SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
```

## Best Practices

1. **Token Management**
   - Use short-lived tokens
   - Implement token refresh
   - Store tokens securely
   - Validate tokens properly

2. **Session Management**
   - Clean up expired sessions
   - Track session activity
   - Implement session revocation
   - Handle concurrent sessions

3. **Error Handling**
   - Log authentication errors
   - Return appropriate status codes
   - Provide clear error messages
   - Handle edge cases

4. **Security**
   - Use HTTPS
   - Implement rate limiting
   - Validate all inputs
   - Follow OWASP guidelines 