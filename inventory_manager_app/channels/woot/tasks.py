"""Woot background task stubs."""

import logging

logger = logging.getLogger(__name__)


class WootTasks:
    """Example Celery task implementations for Woot channel."""

    @staticmethod
    def process_event(event: dict) -> None:
        logger.info("Woot task processing event: %s", event)
