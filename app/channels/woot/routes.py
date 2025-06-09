"""Woot channel routes.

Layer: channels
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from google.oauth2.credentials import Credentials
import logging

from app import db
from app.channels.woot.models import (
    WootPorf,
    WootPo,
    WootPorfStatus,
    WootPoStatus,
    PORF,
    PO,
)
from app.channels.woot.service import WootService, WootOrderService
from app.channels.woot.logic import ingest_porf
from app.core import oauth
from app.core.services.sheets import SheetsService
from app.core.services.drive import DriveService
from app.core.auth.service import AuthService
from app.core.models.user import User
from app.core.models.organisation import Organisation

bp = Blueprint("woot", __name__, url_prefix="/api/woot")
logger = logging.getLogger(__name__)


@bp.route("/porf-upload", methods=["POST"])
def porf_upload():
    """Upload and ingest a PORF spreadsheet."""
    if "file" not in request.files:
        return jsonify({"error": "file required"}), 400
    file = request.files["file"]
    drive = DriveService(None)  # TODO: credentials
    sheets = SheetsService(None)
    result = ingest_porf(file.stream, drive, sheets)
    return jsonify(result), 201


def get_woot_service() -> WootService:
    """Get Woot service instance.

    Returns:
        WootService instance
    """
    # TODO: Integrate with real Google OAuth/session credentials
    # For now, pass None or retrieve from current_user if available
    credentials = None  # Replace with real credential retrieval
    return WootService(credentials)


def get_service() -> WootOrderService:
    """Get the Woot order service instance."""
    session = db.session
    sheets_service = SheetsService(None)  # TODO: Get credentials from config
    return WootOrderService(session, sheets_service)


@bp.route("/porfs", methods=["POST"])
@login_required
def create_porf():
    """Create a new PORF."""
    try:
        data = request.get_json()
        service = get_woot_service()
        porf = service.create_porf(data)
        return jsonify(porf.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating PORF: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/porfs/<int:porf_id>/po", methods=["POST"])
@login_required
def create_po(porf_id: int):
    """Create a new PO from a PORF."""
    try:
        data = request.get_json()
        service = get_woot_service()
        po = service.create_po(porf_id, data)
        return jsonify(po.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating PO: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/pos/<int:po_id>/upload", methods=["POST"])
@login_required
def upload_po_file(po_id: int):
    """Upload a PO file."""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        # Save file temporarily
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        try:
            service = get_woot_service()
            file_id = service.upload_po_file(po_id, file_path)
            return jsonify({"file_id": file_id}), 200
        finally:
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
    except Exception as e:
        current_app.logger.error(f"Error uploading PO file: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/porfs/<int:porf_id>/spreadsheet", methods=["POST"])
@login_required
def create_porf_spreadsheet(porf_id: int):
    """Create a spreadsheet for a PORF."""
    try:
        service = get_woot_service()
        spreadsheet_id = service.create_porf_spreadsheet(porf_id)
        return jsonify({"spreadsheet_id": spreadsheet_id}), 200
    except Exception as e:
        current_app.logger.error(f"Error creating PORF spreadsheet: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/porfs/<int:porf_id>/status", methods=["PUT"])
@login_required
def update_porf_status(porf_id: int):
    """Update a PORF's status."""
    try:
        data = request.get_json()
        status = WootPorfStatus(data["status"])
        service = get_woot_service()
        porf = service.update_porf_status(porf_id, status)
        return jsonify(porf.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error updating PORF status: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/pos/<int:po_id>/status", methods=["PUT"])
@login_required
def update_po_status(po_id: int):
    """Update a PO's status."""
    try:
        data = request.get_json()
        status = WootPoStatus(data["status"])
        service = get_woot_service()
        po = service.update_po_status(po_id, status)
        return jsonify(po.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error updating PO status: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/porfs/<int:porf_id>", methods=["GET"])
@login_required
def get_porf(porf_id: int):
    """Get a PORF by ID."""
    try:
        service = get_woot_service()
        porf = service.get_porf(porf_id)
        return jsonify(porf.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error getting PORF: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/pos/<int:po_id>", methods=["GET"])
@login_required
def get_po(po_id: int):
    """Get a PO by ID."""
    try:
        service = get_woot_service()
        po = service.get_po(po_id)
        return jsonify(po.to_dict()), 200
    except Exception as e:
        current_app.logger.error(f"Error getting PO: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/porfs", methods=["GET"])
@login_required
def list_porfs():
    """List PORFs."""
    try:
        status = request.args.get("status")
        if status:
            status = WootPorfStatus(status)

        service = get_woot_service()
        porfs = service.list_porfs(status)
        return jsonify([porf.to_dict() for porf in porfs]), 200
    except Exception as e:
        current_app.logger.error(f"Error listing PORFs: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/pos", methods=["GET"])
@login_required
def list_pos():
    """List POs."""
    try:
        status = request.args.get("status")
        if status:
            status = WootPoStatus(status)

        service = get_woot_service()
        pos = service.list_pos(status)
        return jsonify([po.to_dict() for po in pos]), 200
    except Exception as e:
        current_app.logger.error(f"Error listing POs: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/orders", methods=["GET"])
def get_orders():
    """Get orders within a date range."""
    start_date = datetime.fromisoformat(request.args.get("start_date"))
    end_date = datetime.fromisoformat(request.args.get("end_date"))

    service = get_service()
    orders = service.fetch_orders(start_date, end_date)
    return jsonify(orders)


@bp.route("/orders", methods=["POST"])
def create_order():
    """Create a new order."""
    data = request.get_json()
    service = get_service()
    order = service.create_order(data)
    return jsonify(order), 201


@bp.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id: str):
    """Get a single order by ID."""
    service = get_service()
    order = service.get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)


@bp.route("/orders/<order_id>", methods=["PUT"])
def update_order(order_id: str):
    """Update an existing order."""
    data = request.get_json()
    service = get_service()
    try:
        order = service.update_order(order_id, data)
        return jsonify(order)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/orders/<order_id>/status", methods=["GET"])
def get_order_status(order_id: str):
    """Get the status of an order."""
    service = get_service()
    try:
        status = service.get_order_status(order_id)
        return jsonify({"status": status})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@bp.route("/export/sheets", methods=["POST"])
def export_to_sheets():
    """Export orders to Google Sheets."""
    data = request.get_json()
    spreadsheet_id = data.get("spreadsheet_id")
    range_name = data.get("range_name")

    if not spreadsheet_id or not range_name:
        return jsonify({"error": "spreadsheet_id and range_name are required"}), 400

    service = get_service()
    service.export_to_sheets(spreadsheet_id, range_name)
    return jsonify({"message": "Export completed successfully"})


@bp.route("/inventory", methods=["GET"])
@login_required
def get_inventory():
    """Get inventory from Woot."""
    try:
        service = get_woot_service()
        inventory = service.fetch_inventory()
        return jsonify(inventory), 200
    except Exception as e:
        current_app.logger.error(f"Error getting inventory: {str(e)}")
        return jsonify({"error": str(e)}), 400


def get_drive_service():
    """Get the Drive service instance."""
    return DriveService(current_user.google_credentials)


def get_sheets_service():
    """Get the Sheets service instance."""
    return SheetsService(current_user.google_credentials)


@bp.route("/workspace", methods=["POST"])
@login_required
def create_workspace():
    """Create a workspace and return its ID."""
    try:
        # Get or create organisation
        org = Organisation.query.filter_by(name=current_user.email.split('@')[0]).first()
        if not org:
            org = Organisation(name=current_user.email.split('@')[0])
            db.session.add(org)
            db.session.commit()
        
        # Create workspace
        drive = get_drive_service()
        workspace_id = drive.ensure_workspace(str(org.id))
        
        # Update organisation with workspace ID
        if org.workspace_folder_id != workspace_id:
            org.workspace_folder_id = workspace_id
            db.session.commit()
        
        return jsonify({"workspace_id": workspace_id}), 201
    
    except Exception as e:
        logger.error("Workspace creation failed: %s", str(e))
        return jsonify({"error": "Failed to create workspace"}), 500


@bp.route("/workspace", methods=["GET"])
@login_required
def get_workspace():
    """Get the current user's workspace ID."""
    try:
        org = Organisation.query.filter_by(name=current_user.email.split('@')[0]).first()
        if not org or not org.workspace_folder_id:
            return jsonify({"error": "Workspace not found"}), 404
        
        return jsonify({"workspace_id": org.workspace_folder_id})
    
    except Exception as e:
        logger.error("Workspace retrieval failed: %s", str(e))
        return jsonify({"error": "Failed to retrieve workspace"}), 500
