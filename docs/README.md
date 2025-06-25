# PO Generator App

A Flask-based application for generating Purchase Orders (POs) with Google Drive integration.

## Overview

The PO Generator App is designed to streamline the process of creating and managing Purchase Orders. It integrates with Google Drive for document storage and Google Sheets for PO templates.

### Key Features

- Google OAuth authentication
- JWT-based session management
- Google Drive integration for document storage
- Google Sheets integration for PO templates
- Multi-organization support
- User role management

## Architecture

The application follows a layered architecture:

```
app/
├── api/          # API endpoints and request handling
├── core/         # Core business logic and services
│   ├── auth/     # Authentication and authorization
│   ├── models/   # Database models
│   └── services/ # Business services
├── channels/     # Channel-specific implementations
└── utils/        # Utility functions and helpers
```

### Key Documents

- [Requirements](./requirements.md) - Key requirements and constraints for the project
- [Improvement Plan](./plan.md) - Detailed plan for enhancing the application
- [API Documentation](./api.md) - Complete API reference
- [Authentication System](./authentication.md) - Authentication flow and implementation
- [Database Models](./database.md) - Database schema and migrations

### Key Components

1. **Authentication**
   - Google OAuth integration
   - JWT token management
   - Session handling

2. **Database**
   - SQLAlchemy ORM
   - Alembic migrations
   - PostgreSQL support

3. **Google Integration**
   - Drive API for document storage
   - Sheets API for PO templates
   - OAuth for authentication

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Google Cloud Project with OAuth credentials

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/po-generator-app.git
   cd po-generator-app
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   flask db upgrade
   ```

### Configuration

Required environment variables:

```env
# Flask
FLASK_APP=app.main:create_app
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database
DATABASE_URL=sqlite:///instance/dev.db

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback/google

# Frontend
FRONTEND_URL=http://localhost:3000
```

## Development

### Running the Application

```bash
flask run
```

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create new migration
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## API Documentation

### Authentication

#### Google OAuth Login
```http
GET /api/auth/google
```

#### OAuth Callback
```http
GET /api/auth/google/callback
```

#### Token Refresh
```http
POST /api/auth/refresh
Authorization: Bearer <token>
```

#### Logout
```http
GET /api/auth/logout
Authorization: Bearer <token>
```

### User Management

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

#### Check Authentication
```http
GET /api/auth/check
Authorization: Bearer <token>
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 
