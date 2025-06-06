from celery import Celery


def create_celery(app):
    """Create a Celery app tied to the Flask application."""
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL"),
        backend=app.config.get("CELERY_RESULT_BACKEND"),
    )
    celery.conf.update(app.config)
    celery.autodiscover_tasks(["tasks.jobs"])
    return celery
