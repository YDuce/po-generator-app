"""Application settings."""

from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Load configuration from environment."""

    model_config = SettingsConfigDict(env_prefix="APP_")

    secret_key: str
    database_url: str = "sqlite:///instance/dev.db"
    max_payload: int = 1024
    redis_url: str = "redis://localhost:6379/0"
    webhook_secrets: list[str] | str = []
    webhook_secrets_file: str | None = None
    service_account_file: str = "secrets/service-account.json"

    def model_post_init(self, __context: Any) -> None:
        if not self.secret_key:
            raise ValueError("APP_SECRET_KEY must not be empty")
        if self.webhook_secrets_file:
            try:
                with open(self.webhook_secrets_file, "r", encoding="utf-8") as f:
                    self.webhook_secrets = [
                        line.strip() for line in f.read().splitlines() if line.strip()
                    ]
            except OSError as exc:
                raise ValueError("unable to load webhook secrets") from exc
        elif isinstance(self.webhook_secrets, str):
            self.webhook_secrets = [s for s in self.webhook_secrets.split(",") if s]
        import os

        if not os.path.exists(self.service_account_file):
            raise ValueError(
                "Service account file not found: " f"{self.service_account_file}"
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
