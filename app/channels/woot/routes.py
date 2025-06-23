from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from .service import WootService

bp = Blueprint("woot", __name__, url_prefix="/api/woot")


@bp.post("/porf")
def create_porf():
    data = request.get_json() or {}
    svc = WootService(db.session)
    try:
        porf = svc.create_porf(data)
        db.session.commit()
    except (ValueError, IntegrityError) as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400
    return jsonify(porf.to_dict()), 201
