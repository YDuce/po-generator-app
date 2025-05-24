from .upload import upload_bp
from .status import status_bp
from .results import results_bp

def register_blueprints(app):
    app.register_blueprint(upload_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(results_bp) 