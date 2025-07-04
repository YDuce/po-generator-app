

def test_create_and_list_reallocation(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app import create_app, db
    from inventory_manager_app.core.config.settings import settings
    from inventory_manager_app.tests.utils import migrate_database, create_token_for
    from inventory_manager_app.core.models import Product

    monkeypatch.setattr(
        settings, "database_url", f"sqlite:///{str(tmp_path / 'test.db')}"
    )
    app = create_app()
    migrate_database(app)
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
