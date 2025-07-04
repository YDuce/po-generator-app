import os

from flask_migrate import upgrade
from sqlalchemy import text
from sqlalchemy.engine.url import make_url


def migrate_database(app) -> None:
    """Apply all Alembic migrations for the given app."""
    with app.app_context():
        from inventory_manager_app import db
        url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
        if (
            url.drivername.startswith("sqlite")
            and url.database
            and os.path.exists(url.database)
        ):
            db.session.remove()
            db.engine.dispose()
            os.remove(url.database)
        # ensure foreign key constraints on SQLite
        db.session.execute(text("PRAGMA foreign_keys=ON"))
        upgrade()


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
