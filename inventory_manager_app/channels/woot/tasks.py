"""Woot background task stubs."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WootTasks:
    """Example Celery task implementations for Woot channel."""

    @staticmethod
    def process_event(event: dict[str, Any]) -> None:
        logger.info("Woot task processing event: %s", event)
