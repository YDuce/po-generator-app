"""Woot utility helpers."""

import logging

logger = logging.getLogger(__name__)


def helper(message: str) -> None:
    logger.info("Woot helper: %s", message)
