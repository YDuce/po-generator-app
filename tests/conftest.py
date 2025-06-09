"""
PyTest fixtures for Woot-MVP.
Runs Alembic migrations against an in-memory SQLite DB
so core tables (product, porf, po …) exist before tests run.
"""

import sys
import os
import tempfile
import importlib.util
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from alembic.config import Config
from alembic import command
from flask_login import FlaskLoginClient
from app.core import oauth
from app.core.oauth import google_bp
from app.api import catalog_bp, export_bp, auth_bp
from app.channels.woot.routes import bp as woot_bp
from tests.test_config import setup_test_environment, TEST_CONFIG

# ------------------------------------------------------------------
# Database – use in-memory SQLite for each test session
# ------------------------------------------------------------------
TEST_DB_URL = TEST_CONFIG['DATABASE_URL']

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine."""
    # Create engine
    eng = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    
    # Run Alembic migrations against the in-memory DB
    alembic_cfg = Config(Path(__file__).resolve().parent.parent / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembbic_cfg, "head")
    
    yield eng
    
    # Cleanup
    eng.dispose()

@pytest.fixture(scope="function")
def db_session(engine):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

# ------------------------------------------------------------------
# Flask app + client that use the same in-memory DB
# ------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.main import create_app

@pytest.fixture(scope="session")
def app(engine):
    """Create and configure a Flask app for testing."""
    # Set up test environment
    setup_test_environment()
    
    # Create app with test config
    application = create_app("app.config.TestingConfig")
    
    # Register blueprints
    application.register_blueprint(google_bp, url_prefix="/auth")
    application.register_blueprint(auth_bp, url_prefix="/api/auth")
    application.register_blueprint(catalog_bp, url_prefix="/api/catalog")
    application.register_blueprint(export_bp, url_prefix="/api/export")
    application.register_blueprint(woot_bp, url_prefix="/api/woot")
    
    return application

@pytest.fixture(scope="function")
def client(app, db_session):
    """Create a test client."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture(scope="function")
def auth_client(app, db_session):
    """Create an authenticated test client with JWT token."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Create test user
            from app.core.models.user import User
            user = User(
                email="test@example.com",
                password_hash="test_hash",
                first_name="Test",
                last_name="User"
            )
            db_session.add(user)
            db_session.commit()
            
            # Create JWT token
            from app.api.auth import create_jwt_token
            token = create_jwt_token(user)
            
            # Set token in headers
            client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
            
            yield client

@pytest.fixture(scope="function")
def oauth_client(app, db_session):
    """Create a test client with mocked OAuth flow."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Create test user
            from app.core.models.user import User
            user = User(
                email="test@example.com",
                password_hash="test_hash",
                first_name="Test",
                last_name="User"
            )
            db_session.add(user)
            db_session.commit()
            
            # Mock OAuth session
            with client.session_transaction() as session:
                session['google_oauth_token'] = {
                    'access_token': 'test_access_token',
                    'token_type': 'Bearer',
                    'expires_in': 3600
                }
                session['user_id'] = user.id
            
            yield client

@pytest.fixture(scope="function")
def mock_drive_service(monkeypatch):
    """Mock the Drive service for testing."""
    class MockDriveService:
        def __init__(self, *args, **kwargs):
            self.created = {}
            self.files = {}
        
        def list_files(self, query=None):
            if query and "name = 'woot'" in query:
                return [{"id": "woot_folder_id"}]
            return []
        
        def create_folder(self, name, parent_id=None):
            folder_id = f"{name}_id"
            self.created[(parent_id, name)] = folder_id
            return {"id": folder_id}
        
        def ensure_workspace(self, org_id):
            return "workspace_id"
        
        def ensure_subfolder(self, parent_id, name):
            return f"{name}_folder_id"
    
    monkeypatch.setattr("app.core.services.drive.DriveService", MockDriveService)
    return MockDriveService()

@pytest.fixture(scope="function")
def mock_sheets_service(monkeypatch):
    """Mock the Sheets service for testing."""
    class MockSheetsService:
        def __init__(self, *args, **kwargs):
            self.created = {}
        
        def copy_template(self, template_id, name, folder_id):
            sheet_id = f"{name}_sheet_id"
            self.created[sheet_id] = {"name": name, "folder_id": folder_id}
            return sheet_id, f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        
        def append_rows(self, sheet_id, rows):
            pass
    
    monkeypatch.setattr("app.core.services.sheets.SheetsService", MockSheetsService)
    return MockSheetsService()
