"""eBay background task stubs."""

import logging

logger = logging.getLogger(__name__)


class EbayTasks:
    """Example Celery task implementations for eBay channel."""

    @staticmethod
    def process_event(event: dict) -> None:
        logger.info("eBay task processing event: %s", event)
