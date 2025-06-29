from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str = Field(..., env="DATABASE_URL")
    secret_key: str
    jwt_secret: str

    celery_broker_url: str
    redis_url: str

    smartsheet_token: str
    smartsheet_webhook_secret: str

    shipstation_api_key: str
    shipstation_api_secret: str
    shipstation_webhook_secret: str | None = Field(
        None, alias="SHIPSTATION_WEBHOOK_SECRET"
    )

    class Config:
        env_file = ".env"
