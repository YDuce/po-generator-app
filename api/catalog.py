from flask import request, jsonify, g
from werkzeug.utils import secure_filename
import os
from logic.catalog_ingest import parse_and_ingest_catalog
from api import api_bp as bp
import logging

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "uploads"
)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@bp.route("/catalog", methods=["POST"])
def upload_catalog():
    if "inventory" not in request.files or "channel" not in request.form:
        logger.warning("Missing file or channel in catalog upload")
        return jsonify({"error": "File and channel are required"}), 400

    inventory = request.files["inventory"]
    channel = request.form["channel"]

    if inventory.filename == "":
        logger.warning("No selected file in catalog upload")
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(inventory.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    inventory.save(file_path)
    logger.info(f"Received catalog file {filename} for channel {channel}")

    try:
        parse_and_ingest_catalog(g.db, file_path, channel)
        logger.info(f"Catalog file {filename} ingested for channel {channel}")
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"File {filename} ingested for channel {channel}",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error during catalog ingestion: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
