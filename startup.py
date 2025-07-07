"""Application startup utilities."""
from __future__ import annotations

from celery import Celery
from google.oauth2.service_account import Credentials

from inventory_manager_app import create_app
from inventory_manager_app.core.services import DriveService, SheetsService
from inventory_manager_app.core.config.settings import get_settings
import redis


def init_celery(app) -> Celery:
    """Configure Celery with Flask application context."""
    celery = Celery(app.import_name, broker="redis://localhost:6379/0")
    celery.conf.update(app.config)
    celery.autodiscover_tasks(["tasks"], force=True)
    celery.conf.beat_schedule = {
        "purge-insights": {
            "task": "tasks.insights.purge_insights",
            "schedule": 90 * 24 * 3600,
        }
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def init_google_services(
    creds_path: str, redis_client: redis.Redis | None = None
) -> tuple[DriveService, SheetsService]:
    creds = Credentials.from_service_account_file(creds_path)
    client = redis_client or redis.Redis.from_url(get_settings().redis_url)
    return DriveService(creds, client), SheetsService(creds, client)


def startup(creds_path: str = "secrets/test-service-key.json") -> tuple:
    app = create_app()
    celery = init_celery(app)
    drive_service, sheets_service = init_google_services(creds_path)
    return app, celery, drive_service, sheets_service


__all__ = [
    "startup",
    "init_celery",
    "init_google_services",
]
