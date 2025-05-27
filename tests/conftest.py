"""
PyTest fixtures for Woot-MVP.
Runs Alembic migrations against an in-memory SQLite DB
so core tables (product, porf, po …) exist before tests run.
"""

from pathlib import Path
import os
import tempfile
import importlib.util

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from alembic.config import Config
from alembic import command

# ------------------------------------------------------------------
# Database – use sqlite:///:memory: for each test session
# ------------------------------------------------------------------
TEST_DB_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

    # Run Alembic migrations against the in-memory DB
    alembic_cfg = Config(Path(__file__).resolve().parent.parent / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembic_cfg, "head")

    yield eng
    eng.dispose()

@pytest.fixture(scope="session")
def db_session(engine):
    """Provide a scoped_session bound to the in-memory engine."""
    Session = scoped_session(sessionmaker(bind=engine))
    yield Session
    Session.remove()

# ------------------------------------------------------------------
# Flask app + client that use the same in-memory DB
# ------------------------------------------------------------------
# Dynamically import create_app from app.py
spec = importlib.util.spec_from_file_location("app", str(Path(__file__).resolve().parent.parent / "app.py"))
app_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_module)
create_app = app_module.create_app

@pytest.fixture(scope="session")
def app(engine):
    os.environ["DATABASE_URL"] = TEST_DB_URL
    application = create_app("testing")
    return application

@pytest.fixture(scope="function")
def client(app):
    return app.test_client() 