import json


def test_shipstation_webhook_bad_sig(client):
    payload = {
        "orderId": "456",
        "orderStatus": "paid",
        "createDate": "2024-01-01T00:00:00",
        "advancedOptions": {"storeId": "ebay"},
        "items": [{"sku": "ABC", "quantity": 1}],
    }
    headers = {"X-ShipStation-Hmac-SHA256": "invalid"}
    resp = client.post(
        "/api/webhook/shipstation",
        data=json.dumps(payload),
        content_type="application/json",
        headers=headers,
    )
    assert resp.status_code == 400
