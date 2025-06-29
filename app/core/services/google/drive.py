"""Google Drive service."""

from typing import Any, BinaryIO, Dict, List, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload


class DriveServiceDisabled(RuntimeError):
    """Raised when Drive operations are attempted without credentials."""


class GoogleDriveService:
    """Service for interacting with Google Drive."""

    def __init__(self, credentials: Credentials | None = None) -> None:
        """Initialize the Google Drive service.

        Args:
            credentials: Google API credentials or ``None`` to disable Drive access
        """
        if credentials is None:
            self.service = None
            self.files = None
            return
        self.service = build("drive", "v3", credentials=credentials)
        self.files = self.service.files()

    @property
    def is_enabled(self) -> bool:
        """Return ``True`` if Drive integration is active."""
        return self.files is not None

    def _require_service(self) -> None:
        if not self.is_enabled:
            raise DriveServiceDisabled("Google Drive service not configured")

    def list_files(self, query: str) -> List[Dict[str, Any]]:
        """List files matching the query."""
        self._require_service()
        results = self.files.list(q=query, fields="files(id,name,parents)").execute()
        return results.get("files", [])

    def get_file(self, file_id: str, fields: str = "*") -> Dict[str, Any]:
        """Get file metadata.

        Args:
            file_id: ID of the file
            fields: Fields to return in the response

        Returns:
            File metadata

        Raises:
            HttpError: If the API request fails
        """
        self._require_service()
        try:
            return self.files.get(fileId=file_id, fields=fields).execute()
        except HttpError as error:
            raise error

    def create_file(
        self, name: str, mime_type: str, parents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new file in Google Drive.

        Args:
            name: Name of the file
            mime_type: MIME type of the file
            parents: Optional list of parent folder IDs

        Returns:
            File metadata

        Raises:
            HttpError: If the API request fails
        """
        self._require_service()
        try:
            file_metadata = {"name": name, "mimeType": mime_type}
            if parents:
                file_metadata["parents"] = parents

            return self.files.create(body=file_metadata, fields="id").execute()
        except HttpError as error:
            raise error

    def upload_file(
        self, file_path: str, mime_type: str, parents: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Upload a file to Google Drive.

        Args:
            file_path: Path to the file to upload
            mime_type: MIME type of the file
            parents: Optional list of parent folder IDs

        Returns:
            File metadata

        Raises:
            HttpError: If the API request fails
        """
        self._require_service()
        try:
            file_metadata = {"name": file_path.split("/")[-1], "mimeType": mime_type}
            if parents:
                file_metadata["parents"] = parents

            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            return self.files.create(body=file_metadata, media_body=media, fields="id").execute()
        except HttpError as error:
            raise error

    def upload_file_from_memory(
        self,
        file_name: str,
        file_content: BinaryIO,
        mime_type: str,
        parents: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Upload a file from memory to Google Drive.

        Args:
            file_name: Name of the file
            file_content: File content as a binary stream
            mime_type: MIME type of the file
            parents: Optional list of parent folder IDs

        Returns:
            File metadata

        Raises:
            HttpError: If the API request fails
        """
        self._require_service()
        try:
            file_metadata = {"name": file_name, "mimeType": mime_type}
            if parents:
                file_metadata["parents"] = parents

            media = MediaIoBaseUpload(file_content, mimetype=mime_type, resumable=True)

            return self.files.create(body=file_metadata, media_body=media, fields="id").execute()
        except HttpError as error:
            raise error

    def update_file(self, file_id: str, file_path: str, mime_type: str) -> Dict[str, Any]:
        """Update an existing file in Google Drive.

        Args:
            file_id: ID of the file to update
            file_path: Path to the new file content
            mime_type: MIME type of the file

        Returns:
            File metadata

        Raises:
            HttpError: If the API request fails
        """
        self._require_service()
        try:
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            return self.files.update(fileId=file_id, media_body=media).execute()
        except HttpError as error:
            raise error

    def delete_file(self, file_id: str) -> None:
        """Delete a file from Google Drive.

        Args:
            file_id: ID of the file to delete

        Raises:
            HttpError: If the API request fails
        """
        self._require_service()
        try:
            self.files.delete(fileId=file_id).execute()
        except HttpError as error:
            raise error

    def create_folder(self, name: str, parent_id: str | None = None) -> Dict[str, Any]:
        """Create a folder and return its metadata."""
        self._require_service()
        metadata: Dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]
        return self.files.create(body=metadata, fields="id,name").execute()

    def ensure_subfolder(self, parent_id: str, name: str) -> str:
        """Return sub-folder ``name`` under ``parent_id``."""
        self._require_service()
        query = (
            f"name = '{name}' and '{parent_id}' in parents and "
            "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        existing = self.list_files(query)
        if existing:
            return existing[0]["id"]

        folder = self.create_folder(name, parent_id)
        return folder["id"]

    def ensure_workspace(self, name: str, *, channels: list[str] | None = None) -> str:
        """Ensure root and optional channel folders exist and return root ID."""
        if not self.is_enabled:
            return ""
        self._require_service()
        query = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        existing = self.list_files(query)
        root_id = existing[0]["id"] if existing else self.create_folder(name)["id"]

        for ch in channels or []:
            sub_q = (
                f"name = '{ch}' and '{root_id}' in parents and "
                "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            )
            if not self.list_files(sub_q):
                self.create_folder(ch, parent_id=root_id)

        return root_id
