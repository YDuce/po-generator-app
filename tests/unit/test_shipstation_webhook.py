from app.core.webhooks.shipstation import parse_order_payload


def test_parse_order_payload():
    payload = {
        "orderId": "123",
        "orderStatus": "paid",
        "createDate": "2024-01-01T00:00:00",
        "advancedOptions": {"storeId": "amazon"},
        "items": [
            {"sku": "ABC", "quantity": 2},
            {"sku": "XYZ", "quantity": 1},
        ],
    }
    order = parse_order_payload(payload)
    assert order["order_id"] == "123"
    assert order["channel"] == "amazon"
    assert order["status"] == "paid"
    assert len(order["items"]) == 2
