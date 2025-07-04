import os
import pytest

from inventory_manager_app.tests.utils import create_test_app, create_token_for


pytestmark = pytest.mark.skipif(
    "POSTGRES_URL" not in os.environ,
    reason="Postgres not available",
)


def test_create_and_list_reallocation(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app import db
    from inventory_manager_app.core.models import Product

    app = create_test_app(tmp_path, monkeypatch)
    with app.app_context():
        prod = Product(
            sku="XYZ",
            name="Prod",
            channel="amazon",
            quantity=0,
        )
        db.session.add(prod)
        db.session.commit()
    token = create_token_for(app)
    headers = {"Authorization": f"Bearer {token}"}
    with app.test_client() as client:
        resp = client.post(
            "/api/v1/reallocations",
            json={"sku": "XYZ", "channel_origin": "amazon", "reason": "slow-mover"},
            headers=headers,
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["sku"] == "XYZ"
        resp = client.get("/api/v1/reallocations", headers=headers)
        assert resp.status_code == 200
        items = resp.get_json()
        assert any(r["sku"] == "XYZ" for r in items)
