"""ShipStation webhook endpoint."""

from flask import Blueprint, request
from uuid import uuid4
from datetime import datetime, timezone
import structlog

from google.oauth2.service_account import Credentials
from ..services.webhook import WebhookService, SheetsService
from ..utils.validation import abort_json
from ..config.settings import get_settings
from ...extensions import db
import redis


bp = Blueprint("shipstation", __name__, url_prefix="/api/v1")


def _service() -> tuple[WebhookService, SheetsService, redis.Redis]:
    settings = get_settings()
    client = redis.Redis.from_url(settings.redis_url)
    service = WebhookService(settings.webhook_secrets, client, db.session)
    creds = Credentials.from_service_account_file(settings.service_account_file)
    sheets = SheetsService(creds, redis_client=client)
    return service, sheets, client


@bp.route("/webhook/shipstation", methods=["POST"])
def handle_webhook() -> tuple[str, int]:
    service, sheets, client = _service()
    key = f"rate:{int(datetime.now(timezone.utc).timestamp())}"
    if client.incr(key) > 100:
        client.expire(key, 1)
        abort_json(429, "Too many requests")
    client.expire(key, 1)
    signature = request.headers.get("X-ShipStation-Signature", "")
    req_id = request.headers.get("X-Request-ID", str(uuid4()))
    structlog.contextvars.bind_contextvars(request_id=req_id)
    msg, code = service.process(
        request.data, signature, request.json or {}, sheets, req_id
    )
    structlog.contextvars.clear_contextvars()
    if code != 204:
        abort_json(code, msg)
    return "", 204
