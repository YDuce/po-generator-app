from __future__ import annotations
from datetime import timedelta
from pydantic import BaseSettings, Field

class _Env(BaseSettings):
    database_url: str = Field("sqlite:///instance/dev.db", env="DATABASE_URL")
    secret_key: str = Field(..., env="SECRET_KEY")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    google_client_id: str | None = None
    google_client_secret: str | None = None
    frontend_url: str | None = None
    cors_origins: str | None = None
    two_way_sync_enabled: bool = Field(False, env="TWO_WAY_SYNC_ENABLED")
    class Config:
        env_file = ".env"

_env = _Env()

class BaseConfig:
    SECRET_KEY = _env.secret_key
    SQLALCHEMY_DATABASE_URI = _env.database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = _env.jwt_secret
    JWT_EXPIRATION = timedelta(days=1)
    GOOGLE_CLIENT_ID = _env.google_client_id
    GOOGLE_CLIENT_SECRET = _env.google_client_secret
    TWO_WAY_SYNC_ENABLED = _env.two_way_sync_enabled

    _cors_raw = _env.cors_origins or (_env.frontend_url or "")
    CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o] or ["*"]

class DevelopmentConfig(BaseConfig):
    DEBUG = True

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(BaseConfig):
    DEBUG = False

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
