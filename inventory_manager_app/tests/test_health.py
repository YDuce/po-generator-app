import os


def test_health_endpoint() -> None:
    os.environ.setdefault("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app import create_app
    app = create_app()
    with app.test_client() as client:
        for path in ["/health", "/api/v1/health"]:
            resp = client.get(path)
            assert resp.status_code == 200
            assert resp.get_json() == {"status": "ok"}
