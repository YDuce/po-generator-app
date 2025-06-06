from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict


class ChannelConnector(ABC):
    """
    Core abstraction for any channel.
    Only declare *universal* operations here.
    """

    @abstractmethod
    def fetch_orders(self, since: datetime) -> List[Dict]:
        """Fetch orders newer than `since`."""
        ...

    @abstractmethod
    def fetch_inventory(self) -> List[Dict]:
        """Fetch current inventory snapshot."""
        ...
