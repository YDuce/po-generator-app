import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from alembic import command
from alembic.config import Config
from app.extensions import db
from app.main import create_app

TEST_DB = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def app():
    os.environ["DATABASE_URL"] = TEST_DB
    application = create_app("testing")
    cfg = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", TEST_DB)
    with application.app_context():
        command.upgrade(cfg, "head")
    yield application
    with application.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
