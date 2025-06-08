"""Order models."""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.models.base import BaseModel

class PurchaseOrder(BaseModel):
    """Purchase order model."""
    
    __tablename__ = 'purchase_orders'
    
    id = Column(Integer, primary_key=True)
    po_number = Column(String(50), unique=True, nullable=False)
    supplier = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default='draft')
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    order_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expected_delivery_date = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    items = relationship('PurchaseOrderItem', back_populates='order', cascade='all, delete-orphan')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurchaseOrder':
        """Create a purchase order from a dictionary.
        
        Args:
            data: Dictionary containing purchase order data
            
        Returns:
            PurchaseOrder instance
        """
        return cls(
            po_number=data.get('po_number'),
            supplier=data.get('supplier'),
            status=data.get('status', 'draft'),
            total_amount=data.get('total_amount'),
            currency=data.get('currency', 'USD'),
            order_date=data.get('order_date', datetime.utcnow()),
            expected_delivery_date=data.get('expected_delivery_date'),
            notes=data.get('notes'),
            extra_data=data.get('extra_data')
        )

class PurchaseOrderItem(BaseModel):
    """Purchase order item model."""
    
    __tablename__ = 'purchase_order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('master_products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    notes = Column(String(500), nullable=True)
    
    # Relationships
    order = relationship('PurchaseOrder', back_populates='items')
    product = relationship('MasterProduct')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurchaseOrderItem':
        """Create a purchase order item from a dictionary.
        
        Args:
            data: Dictionary containing purchase order item data
            
        Returns:
            PurchaseOrderItem instance
        """
        return cls(
            order_id=data.get('order_id'),
            product_id=data.get('product_id'),
            quantity=data.get('quantity'),
            unit_price=data.get('unit_price'),
            total_price=data.get('total_price'),
            notes=data.get('notes')
        )

class PurchaseOrderRequest(BaseModel):
    """Purchase order request model."""
    
    __tablename__ = 'purchase_order_requests'
    
    id = Column(Integer, primary_key=True)
    request_number = Column(String(50), unique=True, nullable=False)
    requester = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False, default='USD')
    request_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    required_by_date = Column(DateTime, nullable=True)
    notes = Column(String(500), nullable=True)
    approved_by = Column(String(100), nullable=True)
    approval_notes = Column(String(500), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_by = Column(String(100), nullable=True)
    rejection_notes = Column(String(500), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)
    
    # Relationships
    items = relationship('PurchaseOrderRequestItem', back_populates='request', cascade='all, delete-orphan')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurchaseOrderRequest':
        """Create a purchase order request from a dictionary.
        
        Args:
            data: Dictionary containing purchase order request data
            
        Returns:
            PurchaseOrderRequest instance
        """
        return cls(
            request_number=data.get('request_number'),
            requester=data.get('requester'),
            status=data.get('status', 'pending'),
            total_amount=data.get('total_amount'),
            currency=data.get('currency', 'USD'),
            request_date=data.get('request_date', datetime.utcnow()),
            required_by_date=data.get('required_by_date'),
            notes=data.get('notes'),
            extra_data=data.get('extra_data')
        )

class PurchaseOrderRequestItem(BaseModel):
    """Purchase order request item model."""
    
    __tablename__ = 'purchase_order_request_items'
    
    id = Column(Integer, primary_key=True)
    request_id = Column(Integer, ForeignKey('purchase_order_requests.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('master_products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    notes = Column(String(500), nullable=True)
    
    # Relationships
    request = relationship('PurchaseOrderRequest', back_populates='items')
    product = relationship('MasterProduct')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurchaseOrderRequestItem':
        """Create a purchase order request item from a dictionary.
        
        Args:
            data: Dictionary containing purchase order request item data
            
        Returns:
            PurchaseOrderRequestItem instance
        """
        return cls(
            request_id=data.get('request_id'),
            product_id=data.get('product_id'),
            quantity=data.get('quantity'),
            unit_price=data.get('unit_price'),
            total_price=data.get('total_price'),
            notes=data.get('notes')
        ) 