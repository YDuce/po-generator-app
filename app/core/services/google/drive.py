"""Google Drive service."""

from typing import List, Dict, Any, Optional, BinaryIO, TypedDict, cast
import os
import json
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)

class FileMetadata(TypedDict):
    """Type for Google Drive file metadata."""
    id: str
    name: str
    mimeType: str
    parents: Optional[List[str]]

class DriveService:
    """Service for interacting with Google Drive."""

    def __init__(self, credentials: Optional[Credentials] = None) -> None:
        """Initialize the Google Drive service.

        Args:
            credentials: Optional Google API credentials. If ``None``, load from
                the ``GOOGLE_SVC_KEY`` environment variable.
        """
        if credentials is None:
            key_json = os.environ.get("GOOGLE_SVC_KEY")
            if not key_json:
                raise ValueError("GOOGLE_SVC_KEY environment variable not set")
            info = json.loads(key_json)
            credentials = service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/drive"],
            )
        elif not credentials.valid:
            raise ValueError("Invalid credentials provided")

        self.service = build("drive", "v3", credentials=credentials)
        self.files = self.service.files()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def list_files(self, query: Optional[str] = None, fields: str = 'files(id, name, mimeType)') -> List[FileMetadata]:
        """List files in Google Drive.
        
        Args:
            query: Optional query to filter files
            fields: Fields to return in the response
            
        Returns:
            List of file metadata
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            results = self.files.list(
                q=query,
                fields=fields
            ).execute()
            return cast(List[FileMetadata], results.get('files', []))
        except HttpError as error:
            logger.error(f"Failed to list files: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_file(self, file_id: str, fields: str = '*') -> FileMetadata:
        """Get file metadata.
        
        Args:
            file_id: ID of the file
            fields: Fields to return in the response
            
        Returns:
            File metadata
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            return cast(FileMetadata, self.files.get(
                fileId=file_id,
                fields=fields
            ).execute())
        except HttpError as error:
            logger.error(f"Failed to get file {file_id}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def create_file(self, name: str, mime_type: str, parents: Optional[List[str]] = None) -> FileMetadata:
        """Create a new file in Google Drive.
        
        Args:
            name: Name of the file
            mime_type: MIME type of the file
            parents: Optional list of parent folder IDs
            
        Returns:
            File metadata
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            file_metadata = {
                'name': name,
                'mimeType': mime_type
            }
            if parents:
                file_metadata['parents'] = parents
            
            return cast(FileMetadata, self.files.create(
                body=file_metadata,
                fields='id'
            ).execute())
        except HttpError as error:
            logger.error(f"Failed to create file {name}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def upload_file(self, file_path: str, mime_type: str, parents: Optional[List[str]] = None) -> FileMetadata:
        """Upload a file to Google Drive.
        
        Args:
            file_path: Path to the file to upload
            mime_type: MIME type of the file
            parents: Optional list of parent folder IDs
            
        Returns:
            File metadata
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
            FileNotFoundError: If the file doesn't exist
        """
        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'mimeType': mime_type
            }
            if parents:
                file_metadata['parents'] = parents
            
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )
            
            return cast(FileMetadata, self.files.create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute())
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except HttpError as error:
            logger.error(f"Failed to upload file {file_path}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def upload_file_from_memory(self, file_name: str, file_content: BinaryIO, mime_type: str, parents: Optional[List[str]] = None) -> FileMetadata:
        """Upload a file from memory to Google Drive.
        
        Args:
            file_name: Name of the file
            file_content: File content as a binary stream
            mime_type: MIME type of the file
            parents: Optional list of parent folder IDs
            
        Returns:
            File metadata
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            file_metadata = {
                'name': file_name,
                'mimeType': mime_type
            }
            if parents:
                file_metadata['parents'] = parents
            
            media = MediaIoBaseUpload(
                file_content,
                mimetype=mime_type,
                resumable=True
            )
            
            return cast(FileMetadata, self.files.create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute())
        except HttpError as error:
            logger.error(f"Failed to upload file from memory {file_name}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def update_file(self, file_id: str, file_path: str, mime_type: str) -> FileMetadata:
        """Update an existing file in Google Drive.
        
        Args:
            file_id: ID of the file to update
            file_path: Path to the new file content
            mime_type: MIME type of the file
            
        Returns:
            File metadata
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
            FileNotFoundError: If the file doesn't exist
        """
        try:
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )
            
            return cast(FileMetadata, self.files.update(
                fileId=file_id,
                media_body=media
            ).execute())
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except HttpError as error:
            logger.error(f"Failed to update file {file_id}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def delete_file(self, file_id: str) -> None:
        """Delete a file from Google Drive.
        
        Args:
            file_id: ID of the file to delete
            
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            self.files.delete(fileId=file_id).execute()
        except HttpError as error:
            logger.error(f"Failed to delete file {file_id}: {error}")
            raise

    def create_folder(self, name: str, parent_id: str) -> FileMetadata:
        """Create a new folder in Google Drive.
        
        Args:
            name: Name of the folder
            parent_id: ID of the parent folder
        Returns:
            File metadata
        Raises:
            HttpError: If the API request fails after retries
            ValueError: If credentials are invalid
        """
        try:
            file_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_id]
            }
            return cast(FileMetadata, self.files.create(
                body=file_metadata,
                fields='id'
            ).execute())
        except HttpError as error:
            logger.error(f"Failed to create folder {name}: {error}")
            raise

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
            folder = self.create_folder(f"Your-App-Workspace-{org_id}", "root")
            root_id = folder["id"]

        woot_id = self.ensure_subfolder(root_id, "woot")
        self.ensure_subfolder(woot_id, "porfs")
        self.ensure_subfolder(woot_id, "pos")
        return root_id

    def ensure_subfolder(self, parent_id: str, path: str) -> str:
        """Ensure subfolder ``path`` exists under ``parent_id`` and return its ID."""
        current = parent_id
        for name in path.split("/"):
            query = (
                f"name = '{name}' and '{current}' in parents and "
                "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            )
            existing = self.list_files(query)
            if existing:
                current = existing[0]["id"]
            else:
                folder = self.create_folder(name, current)
                current = folder["id"]
        return current
