from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io


class DriveService:
    """Core service for interacting with Google Drive."""

    def __init__(self, credentials: Credentials):
        self.service = build("drive", "v3", credentials=credentials)
        self.files = self.service.files()

    def list_files(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in Google Drive, optionally filtered by query."""
        try:
            results = self.files.list(
                q=query, pageSize=100, fields="nextPageToken, files(id, name, mimeType)"
            ).execute()
            return results.get("files", [])
        except HttpError as error:
            raise Exception(f"Error listing files: {error}")

    def get_file(self, file_id: str) -> Dict[str, Any]:
        """Get metadata for a specific file."""
        try:
            return self.files.get(fileId=file_id, fields="id, name, mimeType").execute()
        except HttpError as error:
            raise Exception(f"Error getting file: {error}")

    def download_file(self, file_id: str) -> bytes:
        """Download a file's contents."""
        try:
            request = self.files.get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            return file.getvalue()
        except HttpError as error:
            raise Exception(f"Error downloading file: {error}")

    def upload_file(
        self, file_path: str, mime_type: str, name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Upload a file to Google Drive."""
        try:
            file_metadata = {"name": name}
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            file = self.files.create(
                body=file_metadata, media_body=media, fields="id"
            ).execute()
            return file
        except HttpError as error:
            raise Exception(f"Error uploading file: {error}")

    def delete_file(self, file_id: str) -> None:
        """Delete a file from Google Drive."""
        try:
            self.files.delete(fileId=file_id).execute()
        except HttpError as error:
            raise Exception(f"Error deleting file: {error}")

    def create_folder(
        self, name: str, parent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new folder in Google Drive."""
        try:
            file_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if parent_id:
                file_metadata["parents"] = [parent_id]

            file = self.files.create(body=file_metadata, fields="id").execute()
            return file
        except HttpError as error:
            raise Exception(f"Error creating folder: {error}")

    # ------------------------------------------------------------------
    # Convenience helpers used by channel logic
    # ------------------------------------------------------------------
    def ensure_workspace(self, org_id: str) -> str:
        """Return the workspace folder for an organisation, creating subfolders as needed."""
        query = (
            f"name = 'Your-App-Workspace-{org_id}' and "
            "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        existing = self.list_files(query)
        if existing:
            root_id = existing[0]["id"]
        else:
            folder = self.create_folder(f"Your-App-Workspace-{org_id}")
            root_id = folder["id"]

        # Ensure subfolders under root
        woot_id = self.ensure_subfolder(root_id, "woot")
        self.ensure_subfolder(woot_id, "porfs")
        self.ensure_subfolder(woot_id, "pos")
        return root_id

    def ensure_subfolder(self, parent_id: str, name: str) -> str:
        """Return sub-folder ``name`` under ``parent_id``."""
        query = (
            f"name = '{name}' and '{parent_id}' in parents and "
            "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        )
        existing = self.list_files(query)
        if existing:
            return existing[0]["id"]

        folder = self.create_folder(name, parent_id)
        return folder["id"]
