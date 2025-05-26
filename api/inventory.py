from flask import request, jsonify, g
from werkzeug.utils import secure_filename
import os
from logic.inventory_sync import sync_inventory
from . import bp
import logging

logger = logging.getLogger(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/inventory', methods=['POST'])
def upload_inventory():
    logger.info("Received inventory sync request")
    if 'inventory' in request.files and 'channel' in request.form:
        inventory = request.files['inventory']
        channel = request.form['channel']
        if inventory.filename == '':
            logger.warning("No selected file for inventory upload")
            return jsonify({'error': 'No selected file'}), 400
        filename = secure_filename(inventory.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        inventory.save(file_path)
        import pandas as pd
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
            records = df.to_dict('records')
            sync_inventory(g.db, records, channel)
            logger.info(f"Inventory file {filename} ingested for channel {channel}")
            return jsonify({'status': 'success', 'message': f'File {filename} ingested for channel {channel}'}), 200
        except Exception as e:
            logger.error(f"Error processing inventory file: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    elif request.is_json:
        data = request.get_json()
        channel = data.get('channel')
        records = data.get('records')
        if not channel or not records:
            logger.warning("Missing channel or records in JSON payload")
            return jsonify({'error': 'Channel and records are required'}), 400
        try:
            sync_inventory(g.db, records, channel)
            logger.info(f"Inventory JSON ingested for channel {channel}")
            return jsonify({'status': 'success', 'message': f'Inventory ingested for channel {channel}'}), 200
        except Exception as e:
            logger.error(f"Error processing inventory JSON: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    else:
        logger.warning("Invalid inventory sync request format")
        return jsonify({'error': 'Invalid request format'}), 400 