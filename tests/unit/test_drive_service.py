"""Unit tests for Drive service."""

import pytest
from unittest.mock import patch, MagicMock
from app.core.services.drive import DriveService

class MockDriveAPI:
    """Mock Google Drive API."""
    def __init__(self):
        self.files = {}
        self.folders = {}
    
    def list(self, q=None, spaces='drive', fields='files(id, name)'):
        """Mock list files."""
        if q and 'name = ' in q:
            name = q.split("name = '")[1].split("'")[0]
            if name in self.folders:
                return {'files': [{'id': self.folders[name], 'name': name}]}
        return {'files': []}
    
    def create(self, body=None, fields='id'):
        """Mock create file/folder."""
        if body['mimeType'] == 'application/vnd.google-apps.folder':
            folder_id = f"{body['name']}_id"
            self.folders[body['name']] = folder_id
            return {'id': folder_id}
        return {'id': 'file_id'}

@pytest.fixture
def mock_drive_api():
    """Create mock Drive API."""
    return MockDriveAPI()

@pytest.fixture
def drive_service(mock_drive_api):
    """Create Drive service with mock API."""
    with patch('googleapiclient.discovery.build', return_value=mock_drive_api):
        return DriveService(None)

def test_ensure_workspace(drive_service, mock_drive_api):
    """Test workspace creation."""
    # Create workspace
    workspace_id = drive_service.ensure_workspace('test_org')
    
    # Verify workspace was created
    assert workspace_id == 'Your-App-Workspace-test_org_id'
    assert 'Your-App-Workspace-test_org' in mock_drive_api.folders
    
    # Verify subfolders were created
    assert 'woot' in mock_drive_api.folders
    assert 'porfs' in mock_drive_api.folders
    assert 'pos' in mock_drive_api.folders

def test_ensure_workspace_idempotent(drive_service, mock_drive_api):
    """Test workspace creation is idempotent."""
    # Create workspace twice
    workspace_id1 = drive_service.ensure_workspace('test_org')
    workspace_id2 = drive_service.ensure_workspace('test_org')
    
    # Verify same workspace ID was returned
    assert workspace_id1 == workspace_id2
    assert workspace_id1 == 'Your-App-Workspace-test_org_id'

def test_ensure_subfolder(drive_service, mock_drive_api):
    """Test subfolder creation."""
    # Create subfolder
    folder_id = drive_service.ensure_subfolder('parent_id', 'test_folder')
    
    # Verify subfolder was created
    assert folder_id == 'test_folder_id'
    assert 'test_folder' in mock_drive_api.folders

def test_ensure_subfolder_idempotent(drive_service, mock_drive_api):
    """Test subfolder creation is idempotent."""
    # Create subfolder twice
    folder_id1 = drive_service.ensure_subfolder('parent_id', 'test_folder')
    folder_id2 = drive_service.ensure_subfolder('parent_id', 'test_folder')
    
    # Verify same folder ID was returned
    assert folder_id1 == folder_id2
    assert folder_id1 == 'test_folder_id'

def test_list_files(drive_service, mock_drive_api):
    """Test file listing."""
    # Add test file
    mock_drive_api.folders['test_file'] = 'test_file_id'
    
    # List files
    files = drive_service.list_files("name = 'test_file'")
    
    # Verify file was found
    assert len(files) == 1
    assert files[0]['id'] == 'test_file_id'
    assert files[0]['name'] == 'test_file'

def test_create_folder(drive_service, mock_drive_api):
    """Test folder creation."""
    # Create folder
    folder = drive_service.create_folder('test_folder', 'parent_id')
    
    # Verify folder was created
    assert folder['id'] == 'test_folder_id'
    assert 'test_folder' in mock_drive_api.folders 