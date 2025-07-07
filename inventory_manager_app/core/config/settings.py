"""Application settings."""

from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load configuration from environment."""

    model_config = SettingsConfigDict(env_prefix="APP_")

    secret_key: str
    database_url: str = "sqlite:///inventory.db"
    max_payload: int = 1024

    def model_post_init(self, __context: Any) -> None:  # type: ignore[override]
        if not self.secret_key:
            raise ValueError("APP_SECRET_KEY must not be empty")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
