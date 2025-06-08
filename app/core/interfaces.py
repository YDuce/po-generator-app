from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

class BaseChannelOrderService(ABC):
    """Base interface for channel-specific order services."""
    
    @abstractmethod
    def fetch_orders(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Fetch orders from the channel within the specified date range."""
        pass
    
    @abstractmethod
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order in the channel."""
        pass
    
    @abstractmethod
    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing order in the channel."""
        pass
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get a single order by ID."""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> str:
        """Get the current status of an order."""
        pass

class BaseExportStrategy(ABC):
    """Base interface for export strategies."""
    
    @abstractmethod
    def export(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Export data using the strategy."""
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data before export."""
        pass 