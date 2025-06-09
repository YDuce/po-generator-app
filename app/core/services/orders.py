from typing import Optional, Any
from app.models import PurchaseOrder, PurchaseOrderRequest
from app.extensions import db

class OrdersService:
    def get_order(self, order_id: int) -> Optional[PurchaseOrder]:
        """Get an order by ID."""
        return PurchaseOrder.query.get(order_id)

    def get_orders(self) -> list[PurchaseOrder]:
        """Get all orders."""
        return PurchaseOrder.query.all()

    def create_order(self, data: dict[str, Any]) -> PurchaseOrder:
        """Create a new order."""
        order = PurchaseOrder(**data)
        db.session.add(order)
        db.session.commit()
        return order

    def update_order(self, order_id: int, data: dict[str, Any]) -> PurchaseOrder:
        """Update an order."""
        order = self.get_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        for key, value in data.items():
            setattr(order, key, value)
        db.session.commit()
        return order

    def delete_order(self, order_id: int) -> None:
        """Delete an order."""
        order = self.get_order(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        db.session.delete(order)
        db.session.commit()

    def get_request(self, request_id: int) -> Optional[PurchaseOrderRequest]:
        """Get a request by ID."""
        return PurchaseOrderRequest.query.get(request_id)

    def get_requests(self) -> list[PurchaseOrderRequest]:
        """Get all requests."""
        return PurchaseOrderRequest.query.all()

    def create_request(self, data: dict[str, Any]) -> PurchaseOrderRequest:
        """Create a new request."""
        request = PurchaseOrderRequest(**data)
        db.session.add(request)
        db.session.commit()
        return request

    def update_request(self, request_id: int, data: dict[str, Any]) -> PurchaseOrderRequest:
        """Update a request."""
        request = self.get_request(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        for key, value in data.items():
            setattr(request, key, value)
        db.session.commit()
        return request

    def delete_request(self, request_id: int) -> None:
        """Delete a request."""
        request = self.get_request(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        db.session.delete(request)
        db.session.commit()

    def approve_request(self, request_id: int, approver: str, notes: Optional[str] = None) -> None:
        """Approve a request."""
        request = self.get_request(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        request.approve(approver, notes)
        db.session.commit()

    def reject_request(self, request_id: int, rejector: str, notes: Optional[str] = None) -> None:
        """Reject a request."""
        request = self.get_request(request_id)
        if not request:
            raise ValueError(f"Request {request_id} not found")
        request.reject(rejector, notes)
        db.session.commit() 