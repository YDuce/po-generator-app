from inventory_manager_app import create_app


def test_health_endpoint() -> None:
    app = create_app()
    with app.test_client() as client:
        resp = client.get('/health')
        assert resp.status_code == 200
        assert resp.get_json() == {'status': 'ok'}
