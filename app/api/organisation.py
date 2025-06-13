from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.core.services.google.drive import GoogleDriveService
from app.core.services.organisation import OrganisationService

bp = Blueprint("organisation", __name__)

@bp.post("/create")
def create_org():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("admin_email")
    if not name or not email:
        return jsonify({"error": "name and admin_email required"}), 400

    svc = OrganisationService(GoogleDriveService(current_app.config["GOOGLE_SVC_CREDS"]))
    try:
        org = svc.create_organisation(name, email)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(org.to_dict()), 201
