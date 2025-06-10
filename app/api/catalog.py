"""Catalog API endpoints.

Layer: api
"""

from flask import Blueprint, request, jsonify
from app.core.models.product import MasterProduct, InventoryRecord
from app.core.services.google.sheets import SheetsService
from app import db
from flask import Response

bp = Blueprint('catalog', __name__, url_prefix='/api/catalog')

@bp.route('/products', methods=['GET'])
def get_products() -> Response:
    """Get all products."""
    session = db.session
    products = session.query(MasterProduct).all()
    return jsonify([product.to_dict() for product in products])

@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id: int) -> Response:
    """Get a single product."""
    session = db.session
    product = session.query(MasterProduct).get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify(product.to_dict())

@bp.route('/products', methods=['POST'])
def create_product() -> Response:
    """Create a new product."""
    data = request.get_json()
    session = db.session
    product = MasterProduct.from_dict(data)
    session.add(product)
    session.commit()
    session.refresh(product)
    return jsonify(product.to_dict()), 201

@bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id: int) -> Response:
    """Update a product."""
    data = request.get_json()
    session = db.session
    product = session.query(MasterProduct).get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    for key, value in data.items():
        setattr(product, key, value)
    
    session.commit()
    session.refresh(product)
    return jsonify(product.to_dict())

@bp.route('/inventory', methods=['GET'])
def get_inventory() -> Response:
    """Get inventory records."""
    session = db.session
    records = session.query(InventoryRecord).all()
    return jsonify([record.to_dict() for record in records])

@bp.route('/inventory', methods=['POST'])
def create_inventory_record() -> Response:
    """Create a new inventory record."""
    data = request.get_json()
    session = db.session
    record = InventoryRecord.from_dict(data)
    session.add(record)
    session.commit()
    session.refresh(record)
    return jsonify(record.to_dict()), 201 