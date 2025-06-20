# app/config.py
from __future__ import annotations

import os
import re
from datetime import timedelta
from pathlib import Path
from typing import Final, Literal

from pydantic import AnyHttpUrl, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    "Settings",
    "Development",
    "Testing",
    "Production",
    "CONFIG_MAP",
    "get_settings",
]

_RE_CSV = re.compile(r"\s*,\s*")

# --------------------------------------------------------------------------- #
# Low-level environment parsing                                               #
# --------------------------------------------------------------------------- #


class _EnvSettings(BaseSettings):
    """Single source of truth for raw environment variables."""

    # Core
    DATABASE_URL: str = Field("sqlite:///instance/dev.db", alias="DATABASE_URL")
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    JWT_SECRET: str = Field(..., alias="JWT_SECRET")

    # Optional back-ends
    REDIS_DSN: str | None = Field(None, alias="REDIS_URL")
    CELERY_BROKER_URL: str | None = None  # falls back to REDIS_DSN

    # Third-party credentials
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_SVC_KEY: str | None = None  # raw JSON or path

    # CORS / UI
    FRONTEND_URL: AnyHttpUrl | None = None
    CORS_ORIGINS: str | None = None  # comma-separated list

    # Feature flags
    TWO_WAY_SYNC_ENABLED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        frozen=True,
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _strip_space(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v

    # Helpers
    @property
    def cors_list(self) -> list[str]:
        """Return the normalised CORS allow-list."""
        if self.CORS_ORIGINS:
            cleaned = [o for o in _RE_CSV.split(self.CORS_ORIGINS) if o]
            return cleaned or ["*"]
        if self.FRONTEND_URL:
            return [str(self.FRONTEND_URL)]
        return ["*"]


try:
    _env: Final[_EnvSettings] = _EnvSettings()
except ValidationError as exc:
    raise SystemExit(f"Environment invalid:\n{exc}") from None

# --------------------------------------------------------------------------- #
# Public settings objects                                                     #
# --------------------------------------------------------------------------- #


class Settings:
    """Flattened view of `_EnvSettings` suitable for Flask and Celery."""

    # Flask
    SECRET_KEY = _env.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = _env.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET = _env.JWT_SECRET
    JWT_EXPIRATION = timedelta(days=1)

    # Google
    GOOGLE_CLIENT_ID = _env.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = _env.GOOGLE_CLIENT_SECRET
    GOOGLE_SVC_KEY = _env.GOOGLE_SVC_KEY

    # Feature flags
    TWO_WAY_SYNC_ENABLED = _env.TWO_WAY_SYNC_ENABLED

    # CORS
    CORS_ORIGINS = _env.cors_list

    # Back-ends
    _redis_dsn = _env.REDIS_DSN or "redis://127.0.0.1:6379"
    CELERY_BROKER_URL = _env.CELERY_BROKER_URL or f"{_redis_dsn}/0"
    REDIS_URL = _redis_dsn

    # Misc
    PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Development(Settings):
    DEBUG = True


class Testing(Settings):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class Production(Settings):
    DEBUG = False


_ConfigName = Literal["development", "testing", "production", "default"]

CONFIG_MAP: dict[_ConfigName, type[Settings]] = {
    "development": Development,
    "testing": Testing,
    "production": Production,
    "default": Development,
}


def get_settings(mode: _ConfigName | None = None) -> Settings:
    """Return a Settings instance for the given mode."""
    key = (mode or os.getenv("FLASK_ENV", os.getenv("APP_ENV", "default"))).lower()
    try:
        cls = CONFIG_MAP[key]  # type: ignore[index]
    except KeyError as exc:
        valid = ", ".join(CONFIG_MAP)
        raise ValueError(f"Unknown config '{key}'. Valid keys: {valid}") from exc
    return cls()  # type: ignore[call-arg]
