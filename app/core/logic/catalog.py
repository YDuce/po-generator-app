"""Catalog management logic."""

from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.models.product import MasterProduct, InventoryRecord

class CatalogManager:
    """Manages product catalog and inventory."""
    
    def __init__(self, db: Session):
        """Initialize the catalog manager.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_products(self, filters: Optional[Dict[str, Any]] = None) -> List[MasterProduct]:
        """Get products with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            List of products
        """
        query = self.db.query(MasterProduct)
        if filters:
            if 'sku' in filters:
                query = query.filter(MasterProduct.sku == filters['sku'])
            if 'is_active' in filters:
                query = query.filter(MasterProduct.is_active == filters['is_active'])
        return query.all()
    
    def get_product(self, product_id: int) -> Optional[MasterProduct]:
        """Get a single product by ID.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product if found, None otherwise
        """
        return self.db.query(MasterProduct).get(product_id)
    
    def create_product(self, data: Dict[str, Any]) -> MasterProduct:
        """Create a new product.
        
        Args:
            data: Product data
            
        Returns:
            Created product
        """
        product = MasterProduct.from_dict(data)
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def update_product(self, product_id: int, data: Dict[str, Any]) -> Optional[MasterProduct]:
        """Update a product.
        
        Args:
            product_id: Product ID
            data: Updated product data
            
        Returns:
            Updated product if found, None otherwise
        """
        product = self.get_product(product_id)
        if not product:
            return None
        
        for key, value in data.items():
            setattr(product, key, value)
        
        self.db.commit()
        self.db.refresh(product)
        return product
    
    def get_inventory(self, product_id: Optional[int] = None) -> List[InventoryRecord]:
        """Get inventory records.
        
        Args:
            product_id: Optional product ID to filter by
            
        Returns:
            List of inventory records
        """
        query = self.db.query(InventoryRecord)
        if product_id:
            query = query.filter(InventoryRecord.product_id == product_id)
        return query.all()
    
    def adjust_inventory(self, product_id: int, quantity_delta: int, source: str, notes: Optional[str] = None) -> InventoryRecord:
        """Adjust inventory for a product.
        
        Args:
            product_id: Product ID
            quantity_delta: Quantity change (positive for additions, negative for removals)
            source: Source of the change
            notes: Optional notes
            
        Returns:
            Created inventory record
        """
        record = InventoryRecord(
            product_id=product_id,
            quantity_delta=quantity_delta,
            source=source,
            notes=notes
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record 