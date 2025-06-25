"""Central extension registry."""
from __future__ import annotations

import logging
from celery import Celery
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

__all__ = ["db", "migrate", "cors", "celery_app", "init_celery"]

db = SQLAlchemy()
migrate = Migrate()
cors = CORS()

celery_app = Celery("po_sync_backend", include=["app.tasks.sync"])

logger = logging.getLogger(__name__)


def init_celery(app: Flask) -> None:
    celery_app.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["REDIS_URL"],
        task_default_queue="default",
        task_acks_late=True,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        enable_utc=True,
        timezone="UTC",
    )

    class _CtxTask(celery_app.Task):  # type: ignore[misc]
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super().__call__(*args, **kwargs)

    if not isinstance(celery_app.Task, type):  # idempotent in unit tests
        celery_app.Task = _CtxTask  # type: ignore[assignment]
    logger.info("Celery bound to broker %s", celery_app.conf.broker_url)
