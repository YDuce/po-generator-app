from flask import Blueprint

api_bp = Blueprint("api", __name__)

# import AFTER api_bp is defined so sub-modules can attach routes
from . import catalog, porf, export, status, auth  # noqa: E402


def init_app(app):
    app.register_blueprint(api_bp, url_prefix="/api")
