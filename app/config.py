"""Application configuration utilities.

Layer: app
"""
from __future__ import annotations

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class BaseConfig:
    """Base settings for all environments."""
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Frontend for redirects
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    CORS_ORIGINS = [FRONTEND_URL]

    # JWT settings
    JWT_EXPIRATION = timedelta(days=1)

    # Two-way sync toggle for Sheets writes
    TWO_WAY_SYNC_ENABLED = os.getenv("TWO_WAY_SYNC_ENABLED", "false").lower() == "true"


class DevelopmentConfig(BaseConfig):
    """Settings for local development."""
    DEBUG = True


class ProductionConfig(BaseConfig):
    """Settings for production deployment."""
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

__all__ = [
    "BaseConfig",
    "DevelopmentConfig",
    "ProductionConfig",
    "config",
]
