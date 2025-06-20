# app/extensions.py
"""
Central registry for objects that need late binding to the Flask app.

Anything instantiated here is imported exactly once and then initialised in
`create_app()` to avoid circular-import issues.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from celery import Celery
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

__all__ = ["db", "migrate", "cors", "celery_app", "init_celery"]

db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()
cors: CORS = CORS()

# Celery auto-discovers tasks in app.tasks.*
celery_app: Celery = Celery("po_sync_backend", include=["app.tasks"])

logger = logging.getLogger(__name__)


def init_celery(flask_app: Flask) -> None:
    """Bind Celery to the Flask configuration after `create_app()`."""
    celery_app.conf.update(
        broker_url=flask_app.config["CELERY_BROKER_URL"],
        result_backend=flask_app.config["REDIS_URL"],
        task_acks_late=True,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        enable_utc=True,
        timezone="UTC",
    )

    class FlaskContextTask(celery_app.Task):  # type: ignore[misc]
        """Run tasks inside the Flask application context."""

        abstract = True

        def __call__(self, *args, **kwargs):  # noqa: D401
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery_app.Task = FlaskContextTask  # type: ignore[assignment]
    logger.info("Celery initialised with broker %s", celery_app.conf.broker_url)
