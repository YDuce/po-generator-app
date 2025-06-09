from typing import Optional, Any
from app.models import Product, InventoryItem
from app.extensions import db

class CatalogService:
    def get_product(self, product_id: int) -> Optional[Product]:
        """Get a product by ID."""
        return Product.query.get(product_id)

    def get_products(self) -> list[Product]:
        """Get all products."""
        return Product.query.all()

    def create_product(self, data: dict[str, Any]) -> Product:
        """Create a new product."""
        product = Product(**data)
        db.session.add(product)
        db.session.commit()
        return product

    def update_product(self, product_id: int, data: dict[str, Any]) -> Product:
        """Update a product."""
        product = self.get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return product

    def delete_product(self, product_id: int) -> None:
        """Delete a product."""
        product = self.get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        db.session.delete(product)
        db.session.commit()

    def get_inventory(self) -> list[InventoryItem]:
        """Get all inventory items."""
        return InventoryItem.query.all()

    def create_inventory_record(self, data: dict[str, Any]) -> InventoryItem:
        """Create a new inventory record."""
        inventory_item = InventoryItem(**data)
        db.session.add(inventory_item)
        db.session.commit()
        return inventory_item 