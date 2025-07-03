"""ShipStation webhook endpoint."""

from flask import Blueprint, request, abort

from ..services.webhook import WebhookService
from ..config.settings import settings


bp = Blueprint('shipstation', __name__)
service = WebhookService(secrets=[settings.secret_key])


@bp.route('/api/v1/webhook/shipstation', methods=['POST'])
def handle_webhook() -> tuple[str, int]:
    assert service is not None
    signature = request.headers.get('X-ShipStation-Signature', '')
    if not service.verify(request.data, signature):
        abort(400)
    service.process(request.json or {})
    return '', 204
