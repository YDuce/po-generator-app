from flask import jsonify
from . import bp

@bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    # Placeholder: In a real async setup, look up job status
    return jsonify({'job_id': job_id, 'status': 'complete'}) 