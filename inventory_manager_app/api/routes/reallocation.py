"""Reallocation API routes."""

from flask import Blueprint, jsonify, request

from inventory_manager_app.extensions import db
from inventory_manager_app.core.services.reallocation_repo import (
    ReallocationRepository,
)
from inventory_manager_app.core.utils.auth import require_auth
from inventory_manager_app.core.utils.validation import abort_json, require_fields
from inventory_manager_app.core.models import Product
from inventory_manager_app.core.schemas import NewReallocationPayload

REASONS = {"slow-mover", "out-of-stock"}

bp = Blueprint("reallocation", __name__, url_prefix="/api/v1")


@bp.route("/reallocations", methods=["GET"])
@require_auth("admin")
def list_reallocations() -> tuple[dict, int]:
    """Return recorded reallocations with simple pagination."""
    page = int(request.args.get("page", "1"))
    size = int(request.args.get("size", "50"))
    repo = ReallocationRepository(db.session)
    items = repo.list_paginated(page=page, size=size)
    data = [
        {
            "id": r.id,
            "sku": r.sku,
            "channel_origin": r.channel_origin,
            "reason": r.reason,
            "added_date": r.added_date.isoformat(),
        }
        for r in items
    ]
    return jsonify({"items": data, "page": page, "size": size}), 200


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
    try:

        data_model = NewReallocationPayload.model_validate(payload)
    except Exception as exc:
        abort_json(400, str(exc))

    if not db.session.query(Product).filter_by(sku=data_model.sku).first():
        abort_json(400, "Unknown SKU")
    repo = ReallocationRepository(db.session)
    if repo.exists(data_model.sku, data_model.channel_origin, data_model.reason):
        abort_json(409, "Reallocation exists")
    realloc = repo.create(
        sku=data_model.sku,
        channel_origin=data_model.channel_origin,
        reason=data_model.reason,
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
