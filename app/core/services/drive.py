"""Google Drive service.

Layer: core
"""

import os
import logging
from typing import List, Dict, Any, Optional, BinaryIO, TypedDict, Union
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
import io

logger = logging.getLogger(__name__)

class FileMetadata(TypedDict):
    """Type definition for Google Drive file metadata."""
    id: str
    name: str
    mimeType: str

class DriveService:
    """Google Drive service for file operations."""
    
    def __init__(self, credentials: Optional[Credentials] = None):
        """Initialize Drive service.
        
        Args:
            credentials: Optional Google credentials. If None, loads from GOOGLE_SVC_KEY.
        """
        if credentials is None:
            key_path = os.environ.get("GOOGLE_SVC_KEY")
            if not key_path:
                raise ValueError("GOOGLE_SVC_KEY environment variable not set")
            credentials = Credentials.from_service_account_file(
                key_path,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
        
        self.service = build("drive", "v3", credentials=credentials)
        self.files = self.service.files()
        logger.info("Drive service initialized")

    def list_files(self, folder_id: str) -> List[FileMetadata]:
        """List files in Drive.
        
        Args:
            folder_id: Optional folder ID to list files from
            
        Returns:
            List of file metadata
        """
        query = f"'{folder_id}' in parents" if folder_id else None
        try:
            results = self.files.list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType)"
            ).execute()
            return results.get("files", [])
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise

    def get_file(self, file_id: str, fields: str = '*') -> FileMetadata:
        """Get metadata for a specific file."""
        try:
            return self.files.get(fileId=file_id, fields=fields).execute()
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

    def upload_file(self, file_path: Union[str, BinaryIO], mime_type: str, parents: Optional[list[str]] = None) -> FileMetadata:
        """Upload a file to Google Drive.
        
        Args:
            file_path: Path to file or file-like object
            mime_type: MIME type of the file
            parents: Optional list of parent folder IDs
            
        Returns:
            Uploaded file metadata
        """
        try:
            if isinstance(file_path, str):
                file_metadata = {"name": os.path.basename(file_path)}
                media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            else:
                # Handle file-like object
                file_metadata = {"name": getattr(file_path, 'name', 'uploaded_file')}
                media = MediaIoBaseUpload(file_path, mimetype=mime_type, resumable=True)
                
            if parents:
                file_metadata["parents"] = parents
                
            file = self.files.create(
                body=file_metadata,
                media_body=media,
                fields="id, name, mimeType"
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

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> FileMetadata:
        """Create a folder in Drive.
        
        Args:
            name: Folder name
            parent_id: Optional parent folder ID
            
        Returns:
            Created folder metadata
        """
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if parent_id:
            file_metadata["parents"] = [parent_id]
            
        try:
            file = self.files.create(
                body=file_metadata,
                fields="id, name, mimeType"
            ).execute()
            logger.info(f"Created folder: {name}")
            return file
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            raise

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
