from flask import Blueprint, request, jsonify, current_app
from app.core.services.organisation import OrganisationService

bp = Blueprint('organisation', __name__, url_prefix='/api/organisation')

@bp.route('/create', methods=['POST'])
def create_organisation():
    """Endpoint to onboard a new organisation and admin user."""
    data = request.get_json() or {}
    name = data.get('name')
    admin_email = data.get('admin_email')
    if not name or not admin_email:
        return jsonify({'error': 'name and admin_email are required'}), 400
    try:
        org = OrganisationService.create_organisation(name, admin_email)
        return jsonify(org.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 409
    except Exception as e:
        current_app.logger.error(f"Organisation onboarding failed: {e}")
        return jsonify({'error': 'Internal server error'}), 500
