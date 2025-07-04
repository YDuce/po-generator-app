import os


def test_health_endpoint() -> None:
    os.environ.setdefault("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app import create_app

    app = create_app()
    with app.test_client() as client:
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}
