"""Woot channel actions implementing PORF handling."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WootActions:
    """Actions specific to Woot channel."""

    @staticmethod
    def handle_porfs(data: dict[str, Any]) -> None:
        """Process PORF (Purchase Order Request Form) payloads."""
        logger.info("Woot PORF received: %s", data)
