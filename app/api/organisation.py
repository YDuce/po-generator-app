from flask import Blueprint, request, jsonify, current_app
from flask.typing import ResponseReturnValue
from app.core.services.google.drive import GoogleDriveService
from app.core.services.organisation import OrganisationService

bp = Blueprint("organisation", __name__)

@bp.post("/create")
def create_org() -> ResponseReturnValue:
    data = request.get_json() or {}
    name = data.get("name")
    admin = data.get("admin_email")
    if not name or not admin:
        return jsonify({"error": "name and admin_email required"}), 400

    drive = GoogleDriveService(current_app.config["GOOGLE_SVC_CREDS"])
    try:
        org = OrganisationService(drive).create_organisation(name, admin)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(org.to_dict()), 201
