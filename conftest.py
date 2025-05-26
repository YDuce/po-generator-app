import os
import pytest
from sqlalchemy import create_engine
from alembic import command
from alembic.config import Config
from app import create_app

@pytest.fixture(scope="session")
def app():
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    application = create_app("testing")

    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", "sqlite:///:memory:")
    command.upgrade(cfg, "head")

    yield application

@pytest.fixture
def client(app):
    return app.test_client() 