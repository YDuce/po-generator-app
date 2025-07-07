"""Google Drive management."""

from typing import Any

from googleapiclient.discovery import build

from google.oauth2.service_account import Credentials


class DriveService:
    """Wrapper around the Google Drive API."""

    def __init__(self, creds: Credentials) -> None:
        self.client = build("drive", "v3", credentials=creds, cache_discovery=False)

    def create_folder(self, name: str, parent_id: str | None = None) -> dict[str, Any]:
        metadata = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            metadata["parents"] = [parent_id]
        return self.client.files().create(body=metadata, fields="id").execute()
