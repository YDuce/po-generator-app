import os

from flask_migrate import upgrade


def migrate_database(app) -> None:
    """Apply all Alembic migrations for the given app."""
    with app.app_context():
        upgrade()


def create_test_app(tmp_path, monkeypatch):
    """Create app using POSTGRES_URL for the database."""
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app import create_app
    from inventory_manager_app.core.config.settings import settings

    db_url = os.environ.get("POSTGRES_URL")
    if not db_url:
        raise RuntimeError("POSTGRES_URL not set")
    monkeypatch.setattr(settings, "database_url", db_url)
    app = create_app()
    migrate_database(app)
    return app


def create_token_for(app, email="admin@example.com") -> str:
    """Create a user and return an auth token."""
    with app.app_context():
        from inventory_manager_app import db
        from inventory_manager_app.core.models import Organisation, User
        from inventory_manager_app.core.utils.auth import hash_password, create_token
        from inventory_manager_app.core.config.settings import settings

        org = Organisation.query.get(1)
        if not org:
            org = Organisation(id=1, name="Org", drive_folder_id="1")
            db.session.add(org)
            db.session.commit()
        user = User(
            email=email,
            organisation_id=1,
            password_hash=hash_password("secret"),
            allowed_channels=["admin"],
        )
        db.session.add(user)
        db.session.commit()
        return create_token({"sub": user.id}, settings.secret_key)
