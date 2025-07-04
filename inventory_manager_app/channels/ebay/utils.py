"""eBay utility helpers."""

import logging

logger = logging.getLogger(__name__)


def helper(message: str) -> None:
    logger.info("eBay helper: %s", message)
