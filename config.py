# config.py — single authoritative settings module

from __future__ import annotations
import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Any, Final, List, Optional

from google.oauth2.service_account import Credentials
from pydantic import BaseSettings, Field, model_validator
from pydantic_settings import SettingsConfigDict

# constants
GOOGLE_SCOPES: Final[List[str]] = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]
DEFAULT_CORS: Final[List[str]] = ["*"]


def _extract_cors_list(raw: Optional[str]) -> List[str]:
    if not raw:
        return DEFAULT_CORS.copy()
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


class _EnvSettings(BaseSettings):
    __pydantic_model_config__ = SettingsConfigDict(
        env_file=".env",    # load PROJECT_ROOT/.env
        extra="ignore",     # ignore unrelated env vars
        frozen=True,        # make this settings object immutable
    )

    # core
    database_url: str              = Field("sqlite:///instance/dev.db")
    secret_key:   str              = Field(...)
    jwt_secret:   str              = Field(...)

    # infrastructure
    celery_broker_url: Optional[str] = Field(None)
    redis_url:          Optional[str] = Field(None)

    # third-party APIs
    smartsheet_token:          Optional[str] = Field(None)
    smartsheet_webhook_secret: Optional[str] = Field(None)
    shipstation_api_key:       Optional[str] = Field(None)
    shipstation_api_secret:    Optional[str] = Field(None)

    google_client_id:     Optional[str] = Field(None)
    google_client_secret: Optional[str] = Field(None)
    google_svc_key:       Optional[str] = Field(None)

    # CORS
    frontend_url: Optional[str] = Field(None)
    cors_origins: Optional[str] = Field(None)
    cors_list:    List[str]     = []  # populated below

    # feature flags
    two_way_sync_enabled: bool = Field(False)

    @model_validator(mode="after")
    def _populate_cors_list(self) -> "_EnvSettings":
        raw = self.cors_origins or self.frontend_url
        object.__setattr__(self, "cors_list", _extract_cors_list(raw))
        return self


# parse and validate environment once
_env: Final[_EnvSettings] = _EnvSettings()


def _parse_google_credentials(raw: Optional[str]) -> Credentials:
    """
    Load service-account JSON (inline or file path) and return a
    Credentials instance, or exit if missing/invalid.
    """
    if not raw:
        sys.exit("GOOGLE_SVC_KEY missing — aborting startup.")

    text = Path(raw).read_text(encoding="utf-8") if Path(raw).is_file() else raw
    try:
        key: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError:
        sys.exit("GOOGLE_SVC_KEY must be valid JSON or a path to a JSON file.")

    return Credentials.from_service_account_info(key, scopes=GOOGLE_SCOPES)


# enforce non-None credentials for MyPy
_GOOGLE_CREDS: Final[Credentials] = _parse_google_credentials(_env.google_svc_key)
assert isinstance(_GOOGLE_CREDS, Credentials)


class BaseConfig:
    SECRET_KEY: str   = _env.secret_key
    SQLALCHEMY_DATABASE_URI: str = _env.database_url
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    JWT_SECRET: str          = _env.jwt_secret
    JWT_EXPIRATION: timedelta = timedelta(days=1)

    CELERY_BROKER_URL: Optional[str] = _env.celery_broker_url
    REDIS_URL:          Optional[str] = _env.redis_url

    SMARTSHEET_TOKEN: Optional[str]         = _env.smartsheet_token
    SMARTSHEET_WEBHOOK_SECRET: Optional[str] = _env.smartsheet_webhook_secret

    SHIPSTATION_API_KEY: Optional[str]    = _env.shipstation_api_key
    SHIPSTATION_API_SECRET: Optional[str] = _env.shipstation_api_secret

    GOOGLE_CLIENT_ID: Optional[str]     = _env.google_client_id
    GOOGLE_CLIENT_SECRET: Optional[str] = _env.google_client_secret
    GOOGLE_SVC_CREDS: Credentials       = _GOOGLE_CREDS

    TWO_WAY_SYNC_ENABLED: bool = _env.two_way_sync_enabled
    CORS_ORIGINS: List[str]    = _env.cors_list


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True


class TestingConfig(BaseConfig):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    DEBUG: bool = False


config: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}