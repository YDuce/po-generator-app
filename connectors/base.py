from abc import ABC, abstractmethod
from datetime import datetime

class ChannelConnector(ABC):
    """Canonical interface for every channel connector."""
    @abstractmethod
    def fetch_orders(self, since: datetime) -> list[dict]:
        """Return raw order dicts newer than *since* (UTC)."""
        pass

    @abstractmethod
    def identifier(self) -> str:
        """Return the channel name exactly matching models.channel.name"""
        pass 