"""Reallocation API routes."""

from flask import Blueprint, jsonify, request, abort

from inventory_manager_app.extensions import db
from inventory_manager_app.core.services.reallocation_repo import (
    ReallocationRepository,
)
from inventory_manager_app.core.utils.auth import require_auth
from inventory_manager_app.core.utils.validation import require_fields
from inventory_manager_app.core.models import Product

REASONS = {"slow-mover", "out-of-stock"}

bp = Blueprint("reallocation", __name__, url_prefix="/api/v1")


@bp.route("/reallocations", methods=["GET"])
@require_auth("admin")
def list_reallocations() -> tuple[list[dict], int]:
    """Return all recorded reallocations in chronological order."""
    repo = ReallocationRepository(db.session)
    data = [
        {
            "id": r.id,
            "sku": r.sku,
            "channel_origin": r.channel_origin,
            "reason": r.reason,
            "added_date": r.added_date.isoformat(),
        }
        for r in repo.list_all()
    ]
    return jsonify(data), 200


@bp.route("/reallocations", methods=["POST"])
@require_auth("admin")
def create_reallocation() -> tuple[dict, int]:
    """Create a new reallocation entry if the payload is valid."""
    payload = request.get_json() or {}
    require_fields(
        payload,
        ["sku", "channel_origin", "reason"],
        {"channel_origin": 50, "reason": 255},
    )
    if payload["reason"] not in REASONS:
        abort(400, description="Invalid reason")
    if not db.session.query(Product).filter_by(sku=payload["sku"]).first():
        abort(400, description="Unknown SKU")
    repo = ReallocationRepository(db.session)
    realloc = repo.create(
        sku=payload["sku"],
        channel_origin=payload["channel_origin"],
        reason=payload["reason"],
    )
    db.session.commit()
    data = {
        "id": realloc.id,
        "sku": realloc.sku,
        "channel_origin": realloc.channel_origin,
        "reason": realloc.reason,
        "added_date": realloc.added_date.isoformat(),
    }
    return jsonify(data), 201
