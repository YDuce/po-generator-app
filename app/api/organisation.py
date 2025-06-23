from flask import Blueprint, jsonify, request

from app.core.services.google.drive import GoogleDriveService
from app.core.services.organisation import OrganisationService

bp = Blueprint("organisation", __name__, url_prefix="/api/organisation")


@bp.post("/create")
def create_org():
    data = request.get_json() or {}
    name, admin = data.get("name", "").strip(), data.get("admin_email", "").strip()
    if not name or not admin:
        return jsonify({"error": "name and admin_email required"}), 400

    try:
        drive = GoogleDriveService()  # creds auto-loaded from env
        org = OrganisationService(drive).create(name, admin)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409

    return jsonify(org.to_dict()), 201
