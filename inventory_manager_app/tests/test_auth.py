

def test_login_flow(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app.core.config.settings import settings
    from inventory_manager_app import create_app, db
    from inventory_manager_app.core.models import User
    from inventory_manager_app.tests.utils import migrate_database
    from inventory_manager_app.core.utils.auth import hash_password

    monkeypatch.setattr(
        settings, "database_url", f"sqlite:///{str(tmp_path/'test.db')}"
    )
    app = create_app()
    migrate_database(app)
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=hash_password("secret"),
            organisation_id=1,
        )
        db.session.add(user)
        db.session.commit()
    with app.test_client() as client:
        resp = client.post(
            "/api/v1/login", json={"email": "test@example.com", "password": "secret"}
        )
        assert resp.status_code == 200
        assert "token" in resp.get_json()


def test_auth_decorator(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app.core.config.settings import settings
    from inventory_manager_app import create_app, db
    from inventory_manager_app.core.models import User
    from inventory_manager_app.tests.utils import migrate_database
    from inventory_manager_app.core.utils.auth import hash_password

    monkeypatch.setattr(
        settings, "database_url", f"sqlite:///{str(tmp_path/'test.db')}"
    )
    app = create_app()
    migrate_database(app)
    with app.app_context():
        user = User(
            email="user@example.com",
            password_hash=hash_password("secret"),
            organisation_id=1,
        )
        db.session.add(user)
        db.session.commit()
    with app.test_client() as client:
        resp = client.get("/api/v1/reallocations")
        assert resp.status_code == 401
        token = client.post(
            "/api/v1/login",
            json={"email": "user@example.com", "password": "secret"},
        ).get_json()["token"]
        headers = {"Authorization": f"Bearer {token}"}
        resp = client.get("/api/v1/reallocations", headers=headers)
        assert resp.status_code == 403
