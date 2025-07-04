"""Woot channel actions implementing PORF handling."""

import logging

logger = logging.getLogger(__name__)


class WootActions:
    """Actions specific to Woot channel."""

    @staticmethod
    def handle_porfs(data: dict) -> None:
        """Process PORF (Purchase Order Request Form) payloads."""
        logger.info("Woot PORF received: %s", data)
