"""Order management logic."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.models.order import PurchaseOrder, PurchaseOrderRequest

class OrderManager:
    """Manages purchase orders and requests."""
    
    def __init__(self, db: Session):
        """Initialize the order manager.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_orders(self, filters: Optional[Dict[str, Any]] = None) -> List[PurchaseOrder]:
        """Get purchase orders with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of purchase orders
        """
        query = self.db.query(PurchaseOrder)
        if filters:
            if 'status' in filters:
                query = query.filter(PurchaseOrder.status == filters['status'])
            if 'supplier' in filters:
                query = query.filter(PurchaseOrder.supplier == filters['supplier'])
        return query.all()
    
    def get_order(self, order_id: int) -> Optional[PurchaseOrder]:
        """Get a single purchase order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order if found, None otherwise
        """
        return self.db.query(PurchaseOrder).get(order_id)
    
    def create_order(self, data: Dict[str, Any]) -> PurchaseOrder:
        """Create a new purchase order.
        
        Args:
            data: Order data
            
        Returns:
            Created order
        """
        order = PurchaseOrder.from_dict(data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def update_order(self, order_id: int, data: Dict[str, Any]) -> Optional[PurchaseOrder]:
        """Update a purchase order.
        
        Args:
            order_id: Order ID
            data: Updated order data
            
        Returns:
            Updated order if found, None otherwise
        """
        order = self.get_order(order_id)
        if not order:
            return None
        
        for key, value in data.items():
            setattr(order, key, value)
        
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get_requests(self, filters: Optional[Dict[str, Any]] = None) -> List[PurchaseOrderRequest]:
        """Get purchase order requests with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of purchase order requests
        """
        query = self.db.query(PurchaseOrderRequest)
        if filters:
            if 'status' in filters:
                query = query.filter(PurchaseOrderRequest.status == filters['status'])
            if 'requester' in filters:
                query = query.filter(PurchaseOrderRequest.requester == filters['requester'])
        return query.all()
    
    def get_request(self, request_id: int) -> Optional[PurchaseOrderRequest]:
        """Get a single purchase order request by ID.
        
        Args:
            request_id: Request ID
            
        Returns:
            Request if found, None otherwise
        """
        return self.db.query(PurchaseOrderRequest).get(request_id)
    
    def create_request(self, data: Dict[str, Any]) -> PurchaseOrderRequest:
        """Create a new purchase order request.
        
        Args:
            data: Request data
            
        Returns:
            Created request
        """
        request = PurchaseOrderRequest.from_dict(data)
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
    
    def update_request(self, request_id: int, data: Dict[str, Any]) -> Optional[PurchaseOrderRequest]:
        """Update a purchase order request.
        
        Args:
            request_id: Request ID
            data: Updated request data
            
        Returns:
            Updated request if found, None otherwise
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        for key, value in data.items():
            setattr(request, key, value)
        
        self.db.commit()
        self.db.refresh(request)
        return request
    
    def approve_request(self, request_id: int, approver: str, notes: Optional[str] = None) -> None:
        """Approve a purchase order request.
        
        Args:
            request_id: Request ID
            approver: Name of approver
            notes: Optional approval notes
            
        Returns:
            Updated request if found, None otherwise
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        request.status = 'approved'
        request.approved_by = approver
        request.approval_notes = notes
        request.approved_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(request)
        return request
    
    def reject_request(self, request_id: int, rejector: str, notes: Optional[str] = None) -> None:
        """Reject a purchase order request.
        
        Args:
            request_id: Request ID
            rejector: Name of rejector
            notes: Rejection notes
            
        Returns:
            Updated request if found, None otherwise
        """
        request = self.get_request(request_id)
        if not request:
            return None
        
        request.status = 'rejected'
        request.rejected_by = rejector
        request.rejection_notes = notes
        request.rejected_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(request)
        return request 