from __future__ import annotations

from celery import shared_task

from inventory_manager_app.channels.amazon.tasks import AmazonTasks
from inventory_manager_app.channels.ebay.tasks import EbayTasks
from inventory_manager_app.channels.woot.tasks import WootTasks


_CHANNEL_TASKS = {
    'amazon': AmazonTasks.process_event,
    'ebay': EbayTasks.process_event,
    'woot': WootTasks.process_event,
}


@shared_task
def process_channel_event(channel: str, event: dict) -> None:
    handler = _CHANNEL_TASKS.get(channel)
    if handler:
        handler(event)
