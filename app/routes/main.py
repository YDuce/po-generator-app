"""Main routes."""

from flask import Blueprint, jsonify

main = Blueprint('main', __name__)

@main.route('/health')
def health():
    """Health check endpoint."""
    return jsonify(status='ok') 