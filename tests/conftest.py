import os
import pytest

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("JWT_SECRET", "test")

from app import create_app, db

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
