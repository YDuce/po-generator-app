"""Test helpers."""

from __future__ import annotations

from flask_migrate import upgrade


def create_test_app(tmp_path, monkeypatch):
    """Create app using a temporary database."""
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    monkeypatch.setenv("APP_WEBHOOK_SECRETS", "secret")
    monkeypatch.setenv("APP_DATABASE_URL", "sqlite:///:memory:")
    from inventory_manager_app.core.config.settings import get_settings

    get_settings.cache_clear()
    from inventory_manager_app import create_app

    app = create_app()
    with app.app_context():
        upgrade()

    def teardown() -> None:
        pass

    app.teardown_db = teardown  # type: ignore[attr-defined]

    return app


def create_token_for(app, email="admin@example.com") -> str:
    """Create a user and return an auth token."""
    with app.app_context():
        from inventory_manager_app import db
        from inventory_manager_app.core.models import Organisation, User
        from inventory_manager_app.core.utils.auth import hash_password, create_token
        from inventory_manager_app.core.config.settings import get_settings

        org = Organisation.query.first()
        if not org:
            org = Organisation(name="Org", drive_folder_id="1")
            db.session.add(org)
            db.session.commit()
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                organisation_id=org.id,
                password_hash=hash_password("secret"),
                allowed_channels=["admin"],
            )
            db.session.add(user)
            db.session.commit()
        return create_token({"sub": user.id}, get_settings().secret_key)
