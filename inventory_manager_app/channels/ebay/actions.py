"""eBay channel action stubs that log received events."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EbayActions:
    """Example action implementations for eBay channel."""

    @staticmethod
    def log_event(event: dict[str, Any]) -> None:
        logger.info("eBay event: %s", event)
