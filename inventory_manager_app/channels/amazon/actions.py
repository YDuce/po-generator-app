"""Amazon channel action stubs that log received events."""

import logging

logger = logging.getLogger(__name__)


class AmazonActions:
    """Example action implementations for Amazon channel."""

    @staticmethod
    def log_event(event: dict) -> None:
        logger.info("Amazon event: %s", event)
