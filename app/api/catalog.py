"""Catalog API endpoints."""

from flask import Blueprint, request, jsonify
from app.core.models.product import MasterProduct, InventoryRecord
from app.core.services.sheets import SheetsService
from sqlalchemy.orm import Session

bp = Blueprint('catalog', __name__, url_prefix='/api/catalog')

@bp.route('/products', methods=['GET'])
def get_products():
    """Get all products."""
    db = Session()
    products = db.query(MasterProduct).all()
    return jsonify([product.to_dict() for product in products])

@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id: int):
    """Get a single product."""
    db = Session()
    product = db.query(MasterProduct).get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product.to_dict())

@bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product."""
    data = request.get_json()
    db = Session()
    product = MasterProduct.from_dict(data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return jsonify(product.to_dict()), 201

@bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id: int):
    """Update a product."""
    data = request.get_json()
    db = Session()
    product = db.query(MasterProduct).get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    for key, value in data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return jsonify(product.to_dict())

@bp.route('/inventory', methods=['GET'])
def get_inventory():
    """Get inventory records."""
    db = Session()
    records = db.query(InventoryRecord).all()
    return jsonify([record.to_dict() for record in records])

@bp.route('/inventory', methods=['POST'])
def create_inventory_record():
    """Create a new inventory record."""
    data = request.get_json()
    db = Session()
    record = InventoryRecord.from_dict(data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return jsonify(record.to_dict()), 201 