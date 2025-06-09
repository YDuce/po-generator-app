"""Woot API client implementation."""

from typing import Dict, List, Optional, Any, TypedDict, cast
import requests
from datetime import datetime

class OrderData(TypedDict):
    """Type for Woot order data."""
    id: str
    status: str
    created_at: str
    updated_at: str
    customer: Dict[str, Any]
    items: List[Dict[str, Any]]
    total: float
    currency: str

class InventoryItem(TypedDict):
    """Type for Woot inventory item."""
    id: str
    sku: str
    name: str
    quantity: int
    price: float
    currency: str

class WootClient:
    """Client for interacting with the Woot API."""
    
    def __init__(self, api_key: str, api_url: str = 'https://api.woot.com/v1') -> None:
        """Initialize the Woot client.
        
        Args:
            api_key: Woot API key
            api_url: Base URL for the Woot API
        """
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """Make a request to the Woot API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for requests
            
        Returns:
            API response as dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def get_inventory(self) -> List[InventoryItem]:
        """Get current inventory levels.
        
        Returns:
            List of inventory items
        """
        response = self._make_request('GET', '/inventory')
        return cast(List[InventoryItem], response)
    
    def get_orders(self, start_date: Optional[datetime] = None) -> List[OrderData]:
        """Get orders from Woot.
        
        Args:
            start_date: Optional start date to filter orders
            
        Returns:
            List of orders
        """
        params: Dict[str, str] = {}
        if start_date:
            params['start_date'] = start_date.isoformat()
        
        response = self._make_request('GET', '/orders', params=params)
        return cast(List[OrderData], response)
    
    def create_order(self, order_data: Dict[str, Any]) -> OrderData:
        """Create a new order.
        
        Args:
            order_data: Order data
            
        Returns:
            Created order
        """
        response = self._make_request('POST', '/orders', json=order_data)
        return cast(OrderData, response)
    
    def update_order(self, order_id: str, order_data: Dict[str, Any]) -> OrderData:
        """Update an existing order.
        
        Args:
            order_id: Order ID
            order_data: Updated order data
            
        Returns:
            Updated order
        """
        response = self._make_request('PUT', f'/orders/{order_id}', json=order_data)
        return cast(OrderData, response)
    
    def get_order(self, order_id: str) -> OrderData:
        """Get a single order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order data
        """
        response = self._make_request('GET', f'/orders/{order_id}')
        return cast(OrderData, response)
    
    def get_order_status(self, order_id: str) -> str:
        """Get the status of an order.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order status
        """
        order = self.get_order(order_id)
        return order['status'] 