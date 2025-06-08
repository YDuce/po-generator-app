"""Google Drive service."""

from typing import List, Dict, Any, Optional, BinaryIO
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

class GoogleDriveService:
    """Service for interacting with Google Drive."""
    
    def __init__(self, credentials: Credentials):
        """Initialize the Google Drive service.
        
        Args:
            credentials: Google API credentials
        """
        self.service = build('drive', 'v3', credentials=credentials)
        self.files = self.service.files()
    
    def list_files(self, query: Optional[str] = None, fields: str = 'files(id, name, mimeType)') -> List[Dict[str, Any]]:
        """List files in Google Drive.
        
        Args:
            query: Optional query to filter files
            fields: Fields to return in the response
            
        Returns:
            List of file metadata
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            results = self.files.list(
                q=query,
                fields=fields
            ).execute()
            return results.get('files', [])
        except HttpError as error:
            raise error
    
    def get_file(self, file_id: str, fields: str = '*') -> Dict[str, Any]:
        """Get file metadata.
        
        Args:
            file_id: ID of the file
            fields: Fields to return in the response
            
        Returns:
            File metadata
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            return self.files.get(
                fileId=file_id,
                fields=fields
            ).execute()
        except HttpError as error:
            raise error
    
    def create_file(self, name: str, mime_type: str, parents: Optional[List[str]] = None) -> Dict[str, Any]:
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
        try:
            file_metadata = {
                'name': name,
                'mimeType': mime_type
            }
            if parents:
                file_metadata['parents'] = parents
            
            return self.files.create(
                body=file_metadata,
                fields='id'
            ).execute()
        except HttpError as error:
            raise error
    
    def upload_file(self, file_path: str, mime_type: str, parents: Optional[List[str]] = None) -> Dict[str, Any]:
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
        try:
            file_metadata = {
                'name': file_path.split('/')[-1],
                'mimeType': mime_type
            }
            if parents:
                file_metadata['parents'] = parents
            
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )
            
            return self.files.create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
        except HttpError as error:
            raise error
    
    def upload_file_from_memory(self, file_name: str, file_content: BinaryIO, mime_type: str, parents: Optional[List[str]] = None) -> Dict[str, Any]:
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
            
            return self.files.create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
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
        try:
            media = MediaFileUpload(
                file_path,
                mimetype=mime_type,
                resumable=True
            )
            
            return self.files.update(
                fileId=file_id,
                media_body=media
            ).execute()
        except HttpError as error:
            raise error
    
    def delete_file(self, file_id: str) -> None:
        """Delete a file from Google Drive.
        
        Args:
            file_id: ID of the file to delete
            
        Raises:
            HttpError: If the API request fails
        """
        try:
            self.files.delete(fileId=file_id).execute()
        except HttpError as error:
            raise error 