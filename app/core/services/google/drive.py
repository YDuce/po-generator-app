from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from tenacity import retry, stop_after_attempt, wait_exponential

DRIVE_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


class GoogleDriveService:
    """Minimal wrapper exposing *create folder* and *upload file* operations."""

    def __init__(self, creds: Credentials | None = None) -> None:
        if creds is None:
            raw = os.getenv("GOOGLE_SVC_KEY")
            if raw is None:
                raise RuntimeError("Google Drive credentials not supplied")
            key_data = (
                json.loads(Path(raw).read_text())
                if Path(raw).is_file()
                else json.loads(raw)
            )
            creds = service_account.Credentials.from_service_account_info(
                key_data, scopes=DRIVE_SCOPES
            )

        self._svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        self._files = self._svc.files()

    # ---------------------------------------------------------------- helpers

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def create_folder(
        self,
        name: str,
        parent_id: str | None = None,
    ) -> dict[str, str]:
        body: dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            body["parents"] = [parent_id]
        return self._files.create(body=body, fields="id,name,parents").execute()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def upload_file(
        self,
        path: str | Path,
        mime_type: str,
        parents: list[str] | None = None,
    ) -> dict[str, str]:
        path = Path(path)
        media = MediaFileUpload(path, mimetype=mime_type, resumable=True)
        meta: dict[str, Any] = {"name": path.name, "mimeType": mime_type}
        if parents:
            meta["parents"] = parents
        return self._files.create(
            body=meta, media_body=media, fields="id,webViewLink"
        ).execute()