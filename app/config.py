"""Application configuration.

Layer: app
"""

import os
from datetime import timedelta
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

class BaseConfig:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)  # Use same key for JWT if not specified
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Server configuration
    SERVER_NAME = os.getenv('SERVER_NAME', 'localhost:5000')
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # Frontend URL
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CORS
    CORS_ORIGINS = [FRONTEND_URL]
    
    # Session
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = SECRET_KEY

    TWO_WAY_SYNC_ENABLED = os.getenv('TWO_WAY_SYNC_ENABLED', 'false').lower() == 'true'

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    # Development server settings
    SERVER_NAME = 'localhost:5000'
    PREFERRED_URL_SCHEME = 'http'

class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    TWO_WAY_SYNC_ENABLED = True

class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG = False
    # Ensure secret key is set in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production")
    
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL must be set in production")
    
    # Production server settings
    SERVER_NAME = os.getenv('SERVER_NAME')
    PREFERRED_URL_SCHEME = 'https'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 