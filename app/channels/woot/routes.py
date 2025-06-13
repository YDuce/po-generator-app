from flask import Blueprint, request, jsonify
from .service import WootService

bp = Blueprint("woot", __name__, url_prefix="/api/woot")

@bp.post("/porf")
def create_porf():
    porf = WootService().create_porf(request.get_json())
    return jsonify(porf.to_dict()), 201
