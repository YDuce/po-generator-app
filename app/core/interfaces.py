"""Core interfaces for the application."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypedDict, cast
from datetime import datetime

class OrderData(TypedDict):
    """Type for order data."""
    id: str
    status: str
    created_at: str
    updated_at: str
    total: float
    currency: str

class BaseChannelOrderService(ABC):
    """Base interface for channel-specific order services."""
    
    @abstractmethod
    def fetch_orders(self, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch orders from the channel within the specified date range.
        
        Args:
            start_date: Start date for order fetch
            
        Returns:
            List of orders
        """
        raise NotImplementedError()
    
    @abstractmethod
    def create_order(self, order_data: Dict[str, Any]) -> OrderData:
        """Create a new order in the channel.
        
        Args:
            order_data: Order data
            
        Returns:
            Created order
        """
        raise NotImplementedError()
    
    @abstractmethod
    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> OrderData:
        """Update an existing order in the channel.
        
        Args:
            order_id: Order ID
            order_data: Updated order data
            
        Returns:
            Updated order
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get_order(self, order_id: str) -> Optional[OrderData]:
        """Get a single order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order data if found, None otherwise
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> str:
        """Get the current status of an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status
        """
        raise NotImplementedError()

    @abstractmethod
    def create_porf(self, data: Dict[str, Any]) -> Any:
        """Create a new order in the channel.
        
        Args:
            data: Order data
            
        Returns:
            Created order
        """
        raise NotImplementedError()

    @abstractmethod
    def create_po(self, porf_id: int, data: Dict[str, Any]) -> Any:
        """Create a new order in the channel.
        
        Args:
            porf_id: PORF ID
            data: Order data
            
        Returns:
            Created order
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_inventory(self) -> List[Dict[str, Any]]:
        """Fetch inventory from the channel.
        
        Returns:
            List of inventory items
        """
        raise NotImplementedError()

class ExportResult(TypedDict):
    """Type for export result."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]]

class BaseExportStrategy(ABC):
    """Base interface for export strategies."""
    
    @abstractmethod
    def export(self, data: Dict[str, Any], **kwargs: Any) -> ExportResult:
        """Export data using the strategy.
        
        Args:
            data: Data to export
            **kwargs: Additional arguments
            
        Returns:
            Export result
        """
        raise NotImplementedError()
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate data before export.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        raise NotImplementedError()
