"""Reallocation API routes."""

from flask import Blueprint, Response, jsonify, request
from typing import cast
from sqlalchemy.orm import Session

from inventory_manager_app.extensions import db
from inventory_manager_app.core.services.reallocation_repo import (
    ReallocationRepository,
)
from inventory_manager_app.core.utils.auth import require_auth
from inventory_manager_app.core.utils.validation import abort_json
from inventory_manager_app.core.models import Product
from inventory_manager_app.core.schemas import (
    BatchReallocationPayload,
    NewReallocationPayload,
)

REASONS = {"slow-mover", "out-of-stock"}

bp = Blueprint("reallocation", __name__, url_prefix="/api/v1")


@bp.route("/reallocations", methods=["GET"])
@require_auth("admin")
def list_reallocations() -> tuple[Response, int]:
    """Return recorded reallocations with simple pagination."""
    page = int(request.args.get("page", "1"))
    size = int(request.args.get("size", "50"))
    repo = ReallocationRepository(cast(Session, db.session))
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
def create_reallocation() -> tuple[Response, int]:
    """Create a new reallocation entry if the payload is valid."""
    payload = request.get_json() or {}
    try:
        if "items" in payload:
            data_models = BatchReallocationPayload.model_validate(payload).items
        else:
            data_models = [NewReallocationPayload.model_validate(payload)]
    except Exception as exc:
        abort_json(400, str(exc))

    repo = ReallocationRepository(cast(Session, db.session))
    created = []
    for dm in data_models:
        if not db.session.query(Product).filter_by(sku=dm.sku).first():
            abort_json(400, "Unknown SKU")
        if repo.exists(dm.sku, dm.channel_origin, dm.reason):
            abort_json(409, "Reallocation exists")
        realloc = repo.create(
            sku=dm.sku,
            channel_origin=dm.channel_origin,
            reason=dm.reason,
        )
        created.append(
            {
                "id": realloc.id,
                "sku": realloc.sku,
                "channel_origin": realloc.channel_origin,
                "reason": realloc.reason,
                "added_date": realloc.added_date.isoformat(),
            }
        )
    db.session.commit()
    data = created[0] if len(created) == 1 else {"items": created}
    return jsonify(data), 201
