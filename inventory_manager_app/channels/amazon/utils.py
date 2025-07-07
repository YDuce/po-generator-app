"""Amazon utility helpers."""

import logging

logger = logging.getLogger(__name__)


def helper(message: str) -> None:
    logger.info("Amazon helper: %s", message)
