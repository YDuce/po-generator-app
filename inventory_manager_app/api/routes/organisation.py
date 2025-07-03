"""Organisation routes."""

from flask import Blueprint, jsonify

bp = Blueprint('organisation', __name__)


@bp.route('/api/v1/health')
def health() -> tuple[dict, int]:
    return jsonify({'status': 'ok'}), 200
