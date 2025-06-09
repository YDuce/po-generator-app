"""Export API endpoints.

Layer: api
"""

from flask import Blueprint, request, jsonify
import csv
import os
import tempfile
from google.oauth2 import service_account
from app.core.services.sheets import SheetsService
from app.core.services.drive import DriveService
from app.core.models.product import MasterProduct, InventoryRecord
from app import db

bp = Blueprint("export", __name__, url_prefix="/api/export")


@bp.route("/sheets/products", methods=["POST"])
def export_products_to_sheets():
    """Export products to Google Sheets."""
    data = request.get_json()
    spreadsheet_id = data.get("spreadsheet_id")
    range_name = data.get("range_name")

    if not spreadsheet_id or not range_name:
        return jsonify({"error": "spreadsheet_id and range_name are required"}), 400

    session = db.session
    products = session.query(MasterProduct).all()
    data = [product.to_dict() for product in products]

    key = os.environ.get("GOOGLE_SVC_KEY")
    creds = service_account.Credentials.from_service_account_file(
        key,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    sheets_service = SheetsService(creds)
    sheets_service.update_sheet_data(spreadsheet_id, range_name, data)

    return jsonify({"message": "Export completed successfully"})


@bp.route("/sheets/inventory", methods=["POST"])
def export_inventory_to_sheets():
    """Export inventory records to Google Sheets."""
    data = request.get_json()
    spreadsheet_id = data.get("spreadsheet_id")
    range_name = data.get("range_name")

    if not spreadsheet_id or not range_name:
        return jsonify({"error": "spreadsheet_id and range_name are required"}), 400

    session = db.session
    records = session.query(InventoryRecord).all()
    data = [record.to_dict() for record in records]

    key = os.environ.get("GOOGLE_SVC_KEY")
    creds = service_account.Credentials.from_service_account_file(
        key,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    sheets_service = SheetsService(creds)
    sheets_service.update_sheet_data(spreadsheet_id, range_name, data)

    return jsonify({"message": "Export completed successfully"})


@bp.route("/drive/products", methods=["POST"])
def export_products_to_drive():
    """Export products to Google Drive."""
    data = request.get_json()
    folder_id = data.get("folder_id")
    filename = data.get("filename", "products.csv")

    if not folder_id:
        return jsonify({"error": "folder_id is required"}), 400

    session = db.session
    products = session.query(MasterProduct).all()
    data = [product.to_dict() for product in products]

    with tempfile.NamedTemporaryFile(mode="w+", newline="", delete=False) as tmp:
        writer = csv.DictWriter(tmp, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        csv_path = tmp.name

    key = os.environ.get("GOOGLE_SVC_KEY")
    creds = service_account.Credentials.from_service_account_file(
        key,
        scopes=["https://www.googleapis.com/auth/drive"],
    )
    drive_service = DriveService(creds)
    file = drive_service.upload_file(
        file_path=csv_path, mime_type="text/csv", name=filename
    )

    return jsonify({"message": "Export completed successfully", "file_id": file["id"]})
