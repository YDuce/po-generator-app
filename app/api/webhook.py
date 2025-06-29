"""Webhook endpoints.

Layer: api
"""

from datetime import datetime, timezone
from dateutil.parser import isoparse

from flask import Blueprint, current_app, jsonify, request

from app.core.models import OrderLine, OrderRecord
from app.core.services.sheets import SheetsService
from app.core.webhooks import ShipStationWebhookError, process_webhook
from app.extensions import db

bp = Blueprint("webhook", __name__, url_prefix="/api/webhook")


@bp.route("/shipstation", methods=["POST"])
def shipstation_webhook():
    """Receive ShipStation order webhooks."""
    secret = current_app.config.get("SHIPSTATION_WEBHOOK_SECRET", "")
    signature = request.headers.get("X-ShipStation-Hmac-SHA256", "")

    if not secret or not signature:
        return jsonify({"error": "bad request"}), 400

    payload = request.get_data()
    try:
        order = process_webhook(payload, secret, signature)
    except ShipStationWebhookError:
        return jsonify({"error": "bad request"}), 400
    except Exception:
        return jsonify({"error": "bad request"}), 400

    current_app.logger.info("Received order %s", order["order_id"])

    placed_at_str = order.get("created_at")
    placed_at = isoparse(placed_at_str) if placed_at_str else datetime.now(timezone.utc)

    record = OrderRecord(
        ext_id=order["order_id"],
        channel=order.get("channel", "unknown"),
        status=order.get("status", ""),
        currency=order.get("currency", "USD"),
        total=order.get("total", "0"),
        placed_at=placed_at,
    )
    db.session.add(record)
    for item in order["items"]:
        line = OrderLine(
            order=record,
            sku=item.get("sku", ""),
            quantity=item.get("quantity", 0),
            unit_price=item.get("unit_price"),
        )
        db.session.add(line)
    db.session.commit()

    sheet_id = current_app.config.get("ORDERS_SHEET_ID")
    if sheet_id:
        sheets = SheetsService(None)
        sheets.append_rows(
            sheet_id,
            [[record.ext_id, record.total]],
        )

    return "", 204
