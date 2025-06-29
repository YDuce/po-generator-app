import hmac
from hashlib import sha256

from app.core.models import OrderRecord
from app.extensions import db


def _signature(secret: str, payload: bytes) -> str:
    return hmac.new(secret.encode(), payload, sha256).hexdigest()


def test_shipstation_webhook(client, app):
    secret = "abc"
    app.config["SHIPSTATION_WEBHOOK_SECRET"] = secret
    payload = (
        b'{"orderId":1,"orderDate":"2024-01-01T00:00:00","orderTotal":"10.00",'
        b'"marketplace":"woot","items":[{"sku":"S1","quantity":1,"unitPrice":"10.00"}]}'
    )
    sig = _signature(secret, payload)
    resp = client.post(
        "/api/webhook/shipstation",
        data=payload,
        headers={"X-ShipStation-Hmac-SHA256": sig},
    )
    assert resp.status_code == 204
    with app.app_context():
        assert db.session.query(OrderRecord).count() == 1


def test_shipstation_webhook_invalid_sig(client, app):
    app.config["SHIPSTATION_WEBHOOK_SECRET"] = "abc"
    resp = client.post(
        "/api/webhook/shipstation",
        data=b"{}",
        headers={"X-ShipStation-Hmac-SHA256": "bad"},
    )
    assert resp.status_code == 400
