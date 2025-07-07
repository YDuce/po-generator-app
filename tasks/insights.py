from __future__ import annotations

from datetime import datetime, timedelta, timezone
from celery import shared_task

from inventory_manager_app.extensions import db
from inventory_manager_app.core.models import Insight
from inventory_manager_app.core.services import InsightsService


@shared_task
def generate_insights() -> None:
    service = InsightsService(db.session)
    service.generate()


@shared_task
def purge_insights() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    db.session.query(Insight).filter(Insight.generated_date < cutoff).delete()
    db.session.commit()
