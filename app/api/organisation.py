from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.core.services.google.drive import GoogleDriveService
from app.core.services.organisation import OrganisationService

bp = Blueprint("organisation", __name__, url_prefix="/api/organisation")

@bp.post("/create")
def create_org():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    admin_email = data.get("admin_email", "").strip()

    if not name or not admin_email:
        return jsonify({"error": "name and admin_email required"}), 400

    drive_service = GoogleDriveService(current_app.config["GOOGLE_SVC_CREDS"])
    organisation_service = OrganisationService(drive_service)

    try:
        org = organisation_service.create_organisation(name, admin_email)
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating organisation: {e}")
        return jsonify({"error": "internal server error"}), 500

    return jsonify(org.to_dict()), 201
