from flask import request, jsonify
from werkzeug.utils import secure_filename
import os
from logic.catalog_ingest import parse_and_ingest_catalog
from . import bp

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@bp.route('/upload', methods=['POST'])
def upload_catalog():
    if 'file' not in request.files or 'channel' not in request.form:
        return jsonify({'error': 'File and channel are required'}), 400
    file = request.files['inventory']
    
    channel = request.form['channel']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    try:
        parse_and_ingest_catalog(file_path, channel)
        return jsonify({'status': 'success', 'message': f'File {filename} ingested for channel {channel}'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 