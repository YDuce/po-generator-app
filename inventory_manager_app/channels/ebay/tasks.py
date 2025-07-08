"""eBay background task stubs."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EbayTasks:
    """Example Celery task implementations for eBay channel."""

    @staticmethod
    def process_event(event: dict[str, Any]) -> None:
        logger.info("eBay task processing event: %s", event)
