from __future__ import annotations

import os
import re
from datetime import timedelta
from pathlib import Path
from typing import Final, Literal

from pydantic import AnyHttpUrl, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "Development", "Testing", "Production", "CONFIG_MAP", "get_settings"]

_RE_CSV = re.compile(r"\s*,\s*")


class _EnvSettings(BaseSettings):
    DATABASE_URL: str = Field("sqlite:///instance/dev.db")
    SECRET_KEY: str
    JWT_SECRET: str

    REDIS_DSN: str | None = Field(None, alias="REDIS_URL")
    CELERY_BROKER_URL: str | None = None

    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_SVC_KEY: str | None = None

    FRONTEND_URL: AnyHttpUrl | None = None
    CORS_ORIGINS: str | None = None

    TWO_WAY_SYNC_ENABLED: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", frozen=True, extra="ignore")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _strip_space(cls, v: str | None) -> str | None:
        return v.strip() if isinstance(v, str) else v

    @property
    def cors_list(self) -> list[str]:
        if self.CORS_ORIGINS:
            return [o for o in _RE_CSV.split(self.CORS_ORIGINS) if o] or ["*"]
        if self.FRONTEND_URL:
            return [str(self.FRONTEND_URL)]
        return ["*"]


try:
    _env: Final[_EnvSettings] = _EnvSettings()
except ValidationError as exc:  # pragma: no cover
    raise SystemExit(f"Environment invalid:\n{exc}") from None


class Settings:
    SECRET_KEY = _env.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = _env.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = _env.JWT_SECRET
    JWT_EXPIRATION = timedelta(days=1)

    GOOGLE_CLIENT_ID = _env.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = _env.GOOGLE_CLIENT_SECRET
    GOOGLE_SVC_KEY = _env.GOOGLE_SVC_KEY

    TWO_WAY_SYNC_ENABLED = _env.TWO_WAY_SYNC_ENABLED
    CORS_ORIGINS = _env.cors_list

    _redis_dsn = _env.REDIS_DSN or "redis://127.0.0.1:6379"
    CELERY_BROKER_URL = _env.CELERY_BROKER_URL or f"{_redis_dsn}/0"
    REDIS_URL = _redis_dsn

    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # one directory up from /app


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
    key = (mode or os.getenv("FLASK_ENV", os.getenv("APP_ENV", "default"))).lower()
    try:
        cls = CONFIG_MAP[key]  # type: ignore[index]
    except KeyError as exc:
        raise ValueError(f"Unknown config '{key}'. Valid keys: {', '.join(CONFIG_MAP)}") from exc
    return cls()  # type: ignore[call-arg]