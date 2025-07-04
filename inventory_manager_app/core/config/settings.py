"""Application settings."""

import os
from typing import Any

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Load configuration from environment."""

    secret_key: str = os.getenv("APP_SECRET_KEY", "")
    database_url: str = "sqlite:///inventory.db"
    api_prefix: str = "/api/v1"
    max_payload: int = 1024

    class Config:
        env_prefix = "APP_"

    def model_post_init(self, __context: Any) -> None:  # type: ignore[override]
        if not self.secret_key:
            raise ValueError("APP_SECRET_KEY must not be empty")


settings = Settings()
