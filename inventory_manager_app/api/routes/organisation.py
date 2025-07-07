"""Organisation routes."""

from flask import Blueprint, jsonify, request, url_for, Response
from sqlalchemy.exc import IntegrityError
import structlog

from inventory_manager_app.core.utils.auth import require_auth
from inventory_manager_app.core.utils.validation import (
    require_fields,
    validate_drive_folder_id,
    abort_json,
)
from inventory_manager_app.core.models import Organisation, ChannelSheet
from inventory_manager_app.channels.registry import CHANNELS
from inventory_manager_app.extensions import db
from inventory_manager_app.core.services import DriveService, SheetsService
from inventory_manager_app.core.config.settings import get_settings
from google.oauth2.service_account import Credentials
import redis

logger = structlog.get_logger(__name__)

organisation_bp = Blueprint("organisation", __name__, url_prefix="/api/v1")


@organisation_bp.route("/organisations", methods=["POST"])
@require_auth("admin")
def create_org() -> tuple[Response, int]:
    payload = request.get_json() or {}
    require_fields(payload, ["name", "drive_folder_id"], {"name": 255})
    try:
        validate_drive_folder_id(str(payload["drive_folder_id"]))
    except ValueError as exc:
        abort_json(400, str(exc))
    org = Organisation(name=payload["name"], drive_folder_id=payload["drive_folder_id"])
    db.session.add(org)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort_json(409, "Organisation exists")

    settings = get_settings()
    creds = Credentials.from_service_account_file(settings.service_account_file)
    client = redis.Redis.from_url(settings.redis_url)
    drive = DriveService(creds, client)
    sheets = SheetsService(creds, client)

    for channel in CHANNELS:
        folder = drive.create_folder(channel, parent_id=org.drive_folder_id)
        sheet = sheets.create_spreadsheet(f"{channel}-orders")
        db.session.add(
            ChannelSheet(
                organisation_id=org.id,
                channel=channel,
                folder_id=folder["id"],
                spreadsheet_id=sheet["spreadsheetId"],
            )
        )
    db.session.commit()
    response = jsonify(
        {"id": org.id, "name": org.name, "drive_folder_id": org.drive_folder_id}
    )
    response.headers["Location"] = url_for("organisation.list_orgs", _external=True)
    return response, 201


@organisation_bp.route("/organisations", methods=["GET"])
@require_auth("admin")
def list_orgs() -> tuple[list[dict], int]:
    data = [
        {"id": o.id, "name": o.name, "drive_folder_id": o.drive_folder_id}
        for o in Organisation.query.order_by(Organisation.id).all()
    ]
    return jsonify(data), 200
