from inventory_manager_app.tests.utils import create_test_app


def test_login_flow(tmp_path, monkeypatch):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import User
    from inventory_manager_app.core.utils.auth import hash_password

    app = create_test_app(tmp_path, monkeypatch)
    with app.app_context():
        from inventory_manager_app.core.models import Organisation

        db.session.add(Organisation(id=1, name="Test Org", drive_folder_id="1"))
        db.session.add(
            User(
                email="test@example.com",
                password_hash=hash_password("secret"),
                organisation_id=1,
            )
        )
        db.session.commit()
    with app.test_client() as client:
        resp = client.post(
            "/api/v1/login", json={"email": "test@example.com", "password": "secret"}
        )
        assert resp.status_code == 200
        assert "token" in resp.get_json()
    app.teardown_db()


def test_auth_decorator(tmp_path, monkeypatch):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import User
    from inventory_manager_app.core.utils.auth import hash_password

    app = create_test_app(tmp_path, monkeypatch)
    with app.app_context():
        from inventory_manager_app.core.models import Organisation

        db.session.add(Organisation(id=1, name="Org", drive_folder_id="1"))
        db.session.add(
            User(
                email="user@example.com",
                password_hash=hash_password("secret"),
                organisation_id=1,
            )
        )
        db.session.commit()
    with app.test_client() as client:
        resp = client.get("/api/v1/reallocations")
        assert resp.status_code == 401
        resp = client.get(
            "/api/v1/reallocations",
            headers={"Authorization": "Bearer bad"},
        )
        assert resp.status_code == 401
        token = client.post(
            "/api/v1/login",
            json={"email": "user@example.com", "password": "secret"},
        ).get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/api/v1/reallocations", headers=headers)
        assert resp.status_code == 403
    app.teardown_db()
