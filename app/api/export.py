"""Export API endpoints.

Layer: api
"""

from flask import Blueprint, jsonify, request, current_app

from app.core.models.product import InventoryRecord, MasterProduct
from app.core.services import DriveService
from app.core.services.google.drive import DriveServiceDisabled
from app.core.services.sheets import SheetsService
from app.extensions import db

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

    sheets_service = SheetsService(None)  # TODO: Get credentials from config
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

    sheets_service = SheetsService(None)  # TODO: Get credentials from config
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

    import csv
    from io import BytesIO, StringIO

    output = StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    csv_bytes = BytesIO(output.getvalue().encode())

    drive_service = DriveService(None)  # TODO: Get credentials from config
    try:
        file = drive_service.upload_file_from_memory(
            filename,
            csv_bytes,
            "text/csv",
            parents=[folder_id],
        )
    except DriveServiceDisabled:
        current_app.logger.info("Drive disabled; skipping upload")
        return "", 204

    return jsonify({"message": "Export completed successfully", "file_id": file["id"]})
