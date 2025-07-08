from inventory_manager_app.tests.utils import create_test_app, create_token_for


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
        body = resp.get_json()
        assert any(r["sku"] == "XYZ" for r in body["items"])
    app.teardown_db()


def test_reallocation_invalid_reason(tmp_path, monkeypatch):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import Product

    app = create_test_app(tmp_path, monkeypatch)
    with app.app_context():
        db.session.add(Product(sku="ABC", name="x", channel="amazon"))
        db.session.commit()
    token = create_token_for(app)
    headers = {"Authorization": f"Bearer {token}"}
    with app.test_client() as client:
        resp = client.post(
            "/api/v1/reallocations",
            json={"sku": "ABC", "channel_origin": "amazon", "reason": "bad"},
            headers=headers,
        )
        assert resp.status_code == 400
    app.teardown_db()


def test_reallocation_duplicate(tmp_path, monkeypatch):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import Product

    app = create_test_app(tmp_path, monkeypatch)
    with app.app_context():
        db.session.add(Product(sku="DUP", name="x", channel="amazon"))
        db.session.commit()
    token = create_token_for(app)
    headers = {"Authorization": f"Bearer {token}"}
    with app.test_client() as client:
        assert client.post(
            "/api/v1/reallocations",
            json={"sku": "DUP", "channel_origin": "amazon", "reason": "slow-mover"},
            headers=headers,
        ).status_code == 201
        resp = client.post(
            "/api/v1/reallocations",
            json={"sku": "DUP", "channel_origin": "amazon", "reason": "slow-mover"},
            headers=headers,
        )
        assert resp.status_code == 409
    app.teardown_db()


def _seed_product(app):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import Product

    with app.app_context():
        db.session.add(
            Product(sku="SKU1", name="Prod", channel="amazon", quantity=1)
        )
        db.session.commit()


def test_reallocation_batch(tmp_path, monkeypatch):
    app = create_test_app(tmp_path, monkeypatch)
    _seed_product(app)
    token = create_token_for(app)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "items": [
            {"sku": "SKU1", "channel_origin": "amazon", "reason": "slow-mover"},
            {"sku": "SKU1", "channel_origin": "amazon", "reason": "out-of-stock"},
        ]
    }
    with app.test_client() as client:
        resp = client.post("/api/v1/reallocations", json=payload, headers=headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert len(data["items"]) == 2
    app.teardown_db()


def test_batch_duplicate_fails(tmp_path, monkeypatch):
    app = create_test_app(tmp_path, monkeypatch)
    _seed_product(app)
    token = create_token_for(app)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "items": [
            {"sku": "SKU1", "channel_origin": "amazon", "reason": "slow-mover"},
            {"sku": "SKU1", "channel_origin": "amazon", "reason": "slow-mover"},
        ]
    }
    with app.test_client() as client:
        resp = client.post("/api/v1/reallocations", json=payload, headers=headers)
        assert resp.status_code == 400
        assert "Duplicate reallocation" in resp.get_json()["error"]
    app.teardown_db()
