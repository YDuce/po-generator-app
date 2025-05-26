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
        """Return orders newer than `since`."""
        ...

    @abstractmethod
    def fetch_inventory(self) -> List[Dict]:
        """Return current inventory snapshot for this channel."""
        ...

    @abstractmethod
    def create_batch(self, listings: List[Any], **opts) -> Any:
        """Create a batch (e.g., PO) for the channel from listings."""
        pass

    @abstractmethod
    def submit_batch(self, batch: Any) -> Any:
        """Submit a batch to the channel."""
        pass

    @abstractmethod
    def po_template(self) -> str:
        """Return the relative path under templates/spreadsheets/ for this channel's PO format."""
        pass 