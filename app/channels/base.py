"""Base channel interface.

Layer: channels
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any

class ChannelModel:
    """Base class for channel models."""
    
    def get_channel_name(self) -> str:
        """Get the channel name.
        
        Returns:
            Channel name
        """
        raise NotImplementedError
    
    def get_status_enum(self) -> type:
        """Get the status enum class.
        
        Returns:
            Status enum class
        """
        raise NotImplementedError

class ChannelConnector(ABC):
    """Base class for channel connectors."""
    
    @abstractmethod
    def fetch_orders(self, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch orders from the channel.
        
        Args:
            start_date: Start date for order fetch
            
        Returns:
            List of order data
        """
        raise NotImplementedError()
    
    @abstractmethod
    def fetch_inventory(self) -> List[Dict[str, Any]]:
        """Fetch inventory from the channel.
        
        Returns:
            List of inventory data
        """
        raise NotImplementedError()
    
    @abstractmethod
    def create_porf(self, data: Dict[str, Any]) -> Any:
        """Create a new PORF.
        
        Args:
            data: PORF data
            
        Returns:
            Created PORF instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def create_po(self, porf_id: int, data: Dict[str, Any]) -> Any:
        """Create a new PO from a PORF.
        
        Args:
            porf_id: ID of the PORF to create PO from
            data: Additional PO data
            
        Returns:
            Created PO instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def upload_po_file(self, po_id: int, file_path: str) -> str:
        """Upload a PO file.
        
        Args:
            po_id: ID of the PO
            file_path: Path to the file to upload
            
        Returns:
            ID of the uploaded file
        """
        raise NotImplementedError()
    
    @abstractmethod
    def update_porf_status(self, porf_id: int, status: Any) -> Any:
        """Update a PORF's status.
        
        Args:
            porf_id: ID of the PORF
            status: New status
            
        Returns:
            Updated PORF instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def update_po_status(self, po_id: int, status: Any) -> Any:
        """Update a PO's status.
        
        Args:
            po_id: ID of the PO
            status: New status
            
        Returns:
            Updated PO instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get_porf(self, porf_id: int) -> Any:
        """Get a PORF by ID.
        
        Args:
            porf_id: ID of the PORF
            
        Returns:
            PORF instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get_po(self, po_id: int) -> Any:
        """Get a PO by ID.
        
        Args:
            po_id: ID of the PO
            
        Returns:
            PO instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def list_porfs(self, status: Optional[Any] = None) -> List[Any]:
        """List PORFs.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of PORF instances
        """
        raise NotImplementedError()
    
    @abstractmethod
    def list_pos(self, status: Optional[Any] = None) -> List[Any]:
        """List POs.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of PO instances
        """
        raise NotImplementedError()

class ChannelInterface(ABC):
    """Base interface for channel implementations."""
    
    @abstractmethod
    def create_porf(self, data: Dict[str, Any]) -> Any:
        """Create a new PORF.
        
        Args:
            data: PORF data including lines
            
        Returns:
            Created PORF instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def create_po(self, porf_id: int, data: Dict[str, Any]) -> Any:
        """Create a new PO from a PORF.
        
        Args:
            porf_id: ID of the PORF to create PO from
            data: Additional PO data
            
        Returns:
            Created PO instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def upload_po_file(self, po_id: int, file_path: str) -> str:
        """Upload a PO file.
        
        Args:
            po_id: ID of the PO
            file_path: Path to the file to upload
            
        Returns:
            ID of the uploaded file
        """
        raise NotImplementedError()
    
    @abstractmethod
    def create_porf_spreadsheet(self, porf_id: int) -> str:
        """Create a spreadsheet for a PORF.
        
        Args:
            porf_id: ID of the PORF
            
        Returns:
            ID of the created spreadsheet
        """
        raise NotImplementedError()
    
    @abstractmethod
    def update_porf_status(self, porf_id: int, status: str) -> Any:
        """Update a PORF's status.
        
        Args:
            porf_id: ID of the PORF
            status: New status
            
        Returns:
            Updated PORF instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def update_po_status(self, po_id: int, status: str) -> Any:
        """Update a PO's status.
        
        Args:
            po_id: ID of the PO
            status: New status
            
        Returns:
            Updated PO instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get_porf(self, porf_id: int) -> Any:
        """Get a PORF by ID.
        
        Args:
            porf_id: ID of the PORF
            
        Returns:
            PORF instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def get_po(self, po_id: int) -> Any:
        """Get a PO by ID.
        
        Args:
            po_id: ID of the PO
            
        Returns:
            PO instance
        """
        raise NotImplementedError()
    
    @abstractmethod
    def list_porfs(self, status: Optional[str] = None) -> List[Any]:
        """List PORFs.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of PORF instances
        """
        raise NotImplementedError()
    
    @abstractmethod
    def list_pos(self, status: Optional[str] = None) -> List[Any]:
        """List POs.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of PO instances
        """
        raise NotImplementedError()
    
    @abstractmethod
    def fetch_orders(self, start_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch orders from the channel.
        
        Args:
            start_date: Optional start date for order fetch
            
        Returns:
            List of order data
        """
        raise NotImplementedError()
    
    @abstractmethod
    def fetch_inventory(self) -> List[Dict[str, Any]]:
        """Fetch inventory from the channel.
        
        Returns:
            List of inventory data
        """
        raise NotImplementedError() 