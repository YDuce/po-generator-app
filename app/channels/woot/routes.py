"""Woot channel routes.

Layer: channels
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union, cast
from flask import Blueprint, request, jsonify, current_app, Response
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
from app.core.auth import get_woot_service

bp = Blueprint("woot", __name__, url_prefix="/api/woot")
logger = logging.getLogger(__name__)


@bp.route("/porf-upload", methods=["POST"])
def porf_upload() -> Response:
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


@bp.route("/porf", methods=["POST"])
def create_porf() -> Response:
    """Create a new PORF."""
    try:
        data = request.get_json()
        service = get_woot_service()
        porf = service.create_porf(data)
        return jsonify(porf.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating PORF: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/po", methods=["POST"])
def create_po() -> Response:
    """Create a new PO from a PORF."""
    try:
        data = request.get_json()
        service = get_woot_service()
        po = service.create_po(data['porf_id'], data)
        return jsonify(po.to_dict()), 201
    except Exception as e:
        current_app.logger.error(f"Error creating PO: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/pos/<int:po_id>/upload", methods=["POST"])
@login_required
def upload_po_file(po_id: int) -> Response:
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
def create_porf_spreadsheet(porf_id: int) -> Response:
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
def update_porf_status(porf_id: int) -> Response:
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
def update_po_status(po_id: int) -> Response:
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
def get_porf(porf_id: int) -> Response:
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
def get_po(po_id: int) -> Response:
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
def list_porfs() -> Response:
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
def list_pos() -> Response:
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
def get_orders() -> Tuple[Response, int]:
    """Get orders within a date range."""
    start_date = datetime.fromisoformat(request.args.get("start_date"))
    end_date = datetime.fromisoformat(request.args.get("end_date"))

    service = get_woot_service()
    orders = service.fetch_orders(start_date, end_date)
    return jsonify(orders), 200


@bp.route("/orders", methods=["POST"])
def create_order() -> Tuple[Response, int]:
    """Create a new order."""
    data = request.get_json()
    service = get_woot_service()
    order = service.create_order(data)
    return jsonify(order), 201


@bp.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id: str) -> Tuple[Response, int]:
    """Get a single order by ID."""
    service = get_woot_service()
    order = service.get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200


@bp.route("/orders/<order_id>", methods=["PUT"])
def update_order(order_id: str) -> Tuple[Response, int]:
    """Update an existing order."""
    data = request.get_json()
    service = get_woot_service()
    order = service.update_order(order_id, data)
    return jsonify(order), 200


@bp.route("/orders/<order_id>/status", methods=["GET"])
def get_order_status(order_id: str) -> Tuple[Response, int]:
    """Get the status of an order."""
    service = get_woot_service()
    status = service.get_order_status(order_id)
    return jsonify({"status": status}), 200


@bp.route("/export/sheets", methods=["POST"])
def export_to_sheets() -> Tuple[Response, int]:
    """Export orders to Google Sheets."""
    data = request.get_json()
    spreadsheet_id = data["spreadsheet_id"]
    range_name = data["range_name"]

    service = get_woot_service()
    service.export_to_sheets(spreadsheet_id, range_name)
    return jsonify({"message": "Export completed"}), 200


@bp.route("/inventory", methods=["GET"])
@login_required
def get_inventory() -> Tuple[Response, int]:
    """Get current inventory levels."""
    try:
        service = get_woot_service()
        inventory = service.fetch_inventory()
        return jsonify(inventory), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching inventory: {str(e)}")
        return jsonify({"error": str(e)}), 400


def get_drive_service() -> DriveService:
    """Get Drive service instance."""
    credentials = None  # TODO: Get from session
    return DriveService(credentials)


def get_sheets_service() -> SheetsService:
    """Get Sheets service instance."""
    credentials = None  # TODO: Get from session
    return SheetsService(credentials)


@bp.route("/workspace", methods=["POST"])
@login_required
def create_workspace() -> Tuple[Response, int]:
    """Create a new workspace."""
    try:
        data = request.get_json()
        drive = get_drive_service()
        sheets = get_sheets_service()

        # Create workspace folder
        folder = drive.create_file(
            name=data["name"],
            mime_type="application/vnd.google-apps.folder"
        )

        # Create spreadsheet
        spreadsheet = sheets.create_sheet(f"{data['name']} - Orders")
        spreadsheet_id = spreadsheet["spreadsheetId"]

        return jsonify({
            "folder_id": folder["id"],
            "spreadsheet_id": spreadsheet_id
        }), 201
    except Exception as e:
        current_app.logger.error(f"Error creating workspace: {str(e)}")
        return jsonify({"error": str(e)}), 400


@bp.route("/workspace", methods=["GET"])
@login_required
def get_workspace() -> Tuple[Response, int]:
    """Get workspace details."""
    try:
        drive = get_drive_service()
        sheets = get_sheets_service()

        # Get workspace folder
        folder = drive.get_file(current_app.config["WORKSPACE_FOLDER_ID"])
        if not folder:
            return jsonify({"error": "Workspace not found"}), 404

        # Get spreadsheet
        spreadsheet = sheets.get_sheet_data(
            spreadsheet_id=current_app.config["WORKSPACE_SPREADSHEET_ID"],
            range_name="Sheet1!A1:Z1000"
        )

        return jsonify({
            "folder": folder,
            "spreadsheet": spreadsheet
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error getting workspace: {str(e)}")
        return jsonify({"error": str(e)}), 400
