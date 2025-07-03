"""Application settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Load configuration from environment."""

    secret_key: str = "change-me"
    database_url: str = "sqlite:///inventory.db"

    class Config:
        env_prefix = "APP_"


settings = Settings()
