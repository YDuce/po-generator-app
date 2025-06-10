from flask import Blueprint, jsonify

bp = Blueprint('health', __name__)

@bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}) 