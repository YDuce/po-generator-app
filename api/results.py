from flask import jsonify
from . import bp

@bp.route('/results/<job_id>', methods=['GET'])
def get_results(job_id):
    # Placeholder: In a real async setup, return job results
    return jsonify({'job_id': job_id, 'results': 'Not implemented yet'}) 