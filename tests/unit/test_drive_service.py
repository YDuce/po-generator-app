"""Unit tests for Drive service."""

import pytest
from unittest.mock import patch, MagicMock
from app.core.services.drive import DriveService


class MockDriveAPI:
    """Mock Google Drive API."""

    def __init__(self):
        self.folders = {}
        self.uploaded = []

    def files(self):
        return self

    class _Request:
        def __init__(self, data):
            self.data = data

        def execute(self):
            return self.data

    def list(self, q=None, pageSize=100, fields="files(id, name, mimeType)"):
        """Mock list files."""
        if q and "name = " in q:
            name = q.split("name = '")[1].split("'")[0]
            if name in self.folders:
                return self._Request(
                    {"files": [{"id": self.folders[name], "name": name}]}
                )
        return self._Request({"files": []})

    def create(self, body=None, media_body=None, fields="id"):
        """Mock create file/folder."""
        mime = body.get("mimeType")
        if mime == "application/vnd.google-apps.folder":
            folder_id = f"{body['name']}_id"
            self.folders[body["name"]] = folder_id
            return self._Request({"id": folder_id})
        file_id = f"{body['name']}_id"
        self.uploaded.append({"id": file_id, "name": body["name"], "mimeType": mime})
        return self._Request({"id": file_id})


@pytest.fixture
def mock_drive_api():
    """Create mock Drive API."""
    return MockDriveAPI()


@pytest.fixture
def drive_service(mock_drive_api):
    """Create Drive service with mock API."""
    with patch("app.core.services.drive.build", return_value=mock_drive_api), patch(
        "google.oauth2.service_account.Credentials.from_service_account_file",
        return_value=MagicMock(valid=True),
    ):
        return DriveService(None)


def test_ensure_workspace(drive_service, mock_drive_api) -> None:
    """Test workspace creation."""
    # Create workspace
    workspace_id = drive_service.ensure_workspace("test_org")

    # Verify workspace was created
    assert workspace_id == "Your-App-Workspace-test_org_id"
    assert "Your-App-Workspace-test_org" in mock_drive_api.folders

    # Verify subfolders were created
    assert "woot" in mock_drive_api.folders
    assert "porfs" in mock_drive_api.folders
    assert "pos" in mock_drive_api.folders


def test_ensure_workspace_idempotent(drive_service, mock_drive_api) -> None:
    """Test workspace creation is idempotent."""
    # Create workspace twice
    workspace_id1 = drive_service.ensure_workspace("test_org")
    workspace_id2 = drive_service.ensure_workspace("test_org")

    # Verify same workspace ID was returned
    assert workspace_id1 == workspace_id2
    assert workspace_id1 == "Your-App-Workspace-test_org_id"


def test_ensure_subfolder(drive_service, mock_drive_api) -> None:
    """Test subfolder creation."""
    # Create subfolder
    folder_id = drive_service.ensure_subfolder("parent_id", "test_folder")

    # Verify subfolder was created
    assert folder_id == "test_folder_id"
    assert "test_folder" in mock_drive_api.folders


def test_ensure_subfolder_idempotent(drive_service, mock_drive_api) -> None:
    """Test subfolder creation is idempotent."""
    # Create subfolder twice
    folder_id1 = drive_service.ensure_subfolder("parent_id", "test_folder")
    folder_id2 = drive_service.ensure_subfolder("parent_id", "test_folder")

    # Verify same folder ID was returned
    assert folder_id1 == folder_id2
    assert folder_id1 == "test_folder_id"


def test_list_files(drive_service, mock_drive_api) -> None:
    """Test file listing."""
    # Add test file
    mock_drive_api.folders["test_file"] = "test_file_id"

    # List files
    files = drive_service.list_files("name = 'test_file'")

    # Verify file was found
    assert len(files) == 1
    assert files[0]["id"] == "test_file_id"
    assert files[0]["name"] == "test_file"


def test_create_folder(drive_service, mock_drive_api) -> None:
    """Test folder creation."""
    # Create folder
    folder = drive_service.create_folder("test_folder", "parent_id")

    # Verify folder was created
    assert folder["id"] == "test_folder_id"
    assert "test_folder" in mock_drive_api.folders


def test_drive_service_init() -> None:
    """Ensure service initializes with provided credentials."""
    creds = object()
    with patch("googleapiclient.discovery.build") as build_mock:
        service = DriveService(creds)
        build_mock.assert_called_once_with("drive", "v3", credentials=creds)
        assert service.files


def test_drive_service_upload_file(tmp_path) -> None:
    """Test uploading a file uses the correct name."""
    api = MockDriveAPI()
    with patch("app.core.services.drive.build", return_value=api), patch(
        "google.oauth2.service_account.Credentials.from_service_account_file",
        return_value=MagicMock(valid=True),
    ):
        service = DriveService(None)
    file_path = tmp_path / "example.txt"
    file_path.write_text("")
    result = service.upload_file(str(file_path), "text/plain")
    assert result["id"] == "example.txt_id"
    assert api.uploaded[0]["name"] == "example.txt"


def test_drive_service_upload_file_custom_name(tmp_path) -> None:
    """Upload with an explicit name override."""
    api = MockDriveAPI()
    with patch("app.core.services.drive.build", return_value=api), patch(
        "google.oauth2.service_account.Credentials.from_service_account_file",
        return_value=MagicMock(valid=True),
    ):
        service = DriveService(None)
    file_path = tmp_path / "foo.txt"
    file_path.write_text("data")
    result = service.upload_file(str(file_path), "text/plain", name="bar.txt")
    assert result["id"] == "bar.txt_id"
    assert api.uploaded[0]["name"] == "bar.txt"


def test_drive_service_download_file() -> None:
    pass
