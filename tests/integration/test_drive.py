import pytest
from unittest.mock import patch, MagicMock
from app.core.services.google.drive import DriveService
from app.core.services.google.sheets import SheetsService
from app.models.user import User
from app import db

@pytest.fixture
def mock_drive_service():
    """Create a mock DriveService with realistic behavior."""
    with patch('app.core.services.google.drive.DriveService') as mock:
        service = mock.return_value
        service.list_files.return_value = []
        service.create_folder.return_value = {'id': 'mock_folder_id'}
        service.upload_file.return_value = {'id': 'mock_file_id'}
        yield service

@pytest.fixture
def mock_sheets_service():
    """Create a mock SheetsService with realistic behavior."""
    with patch('app.core.services.google.sheets.SheetsService') as mock:
        service = mock.return_value
        service.create_spreadsheet.return_value = {'id': 'mock_sheet_id'}
        yield service

def test_workspace_creation(client, db_session, mock_drive_service, mock_sheets_service) -> None:
    """Test complete workspace creation flow."""
    # Create test user
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Request workspace creation
    response = client.post('/api/workspace')
    assert response.status_code == 201
    workspace_id = response.json['workspace_id']
    
    # Verify workspace structure was created
    mock_drive_service.ensure_workspace.assert_called_once()
    mock_drive_service.ensure_subfolder.assert_any_call(workspace_id, 'woot')
    mock_drive_service.ensure_subfolder.assert_any_call(workspace_id, 'porfs')
    mock_drive_service.ensure_subfolder.assert_any_call(workspace_id, 'pos')

def test_porf_upload_flow(client, db_session, mock_drive_service, mock_sheets_service) -> None:
    """Test complete PORF upload and processing flow."""
    # Create test user and workspace
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Create test file content
    test_content = b'Test PORF content'
    
    # Upload PORF
    response = client.post(
        '/api/woot/porf-upload',
        data={'file': (test_content, 'test.porf')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 201
    porf_id = response.json['porf_id']
    
    # Verify file was uploaded to correct location
    mock_drive_service.upload_file.assert_called_once()
    upload_args = mock_drive_service.upload_file.call_args[1]
    assert upload_args['name'] == 'test.porf'
    
    # Verify spreadsheet was created
    mock_sheets_service.create_spreadsheet.assert_called_once()

def test_error_handling(client, db_session, mock_drive_service) -> None:
    """Test error handling in Drive operations."""
    # Create test user
    user = User(
        email='test@example.com',
        name='Test User',
        google_id='123456789'
    )
    db_session.add(user)
    db_session.commit()
    
    # Login user
    with client.session_transaction() as session:
        session['user_id'] = user.id
    
    # Simulate Drive API error
    mock_drive_service.ensure_workspace.side_effect = Exception('Drive API Error')
    
    # Attempt workspace creation
    response = client.post('/api/workspace')
    assert response.status_code == 500
    assert 'error' in response.json 