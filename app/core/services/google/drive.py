"""Minimal Drive wrapper for folders, uploads, and sharing."""
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

_DRIVE_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]


def _default_creds() -> Credentials:
    raw = os.getenv("GOOGLE_SVC_KEY")
    if raw is None:
        raise RuntimeError("Google Drive credentials not supplied")
    key_data = (
        json.loads(Path(raw).read_text()) if Path(raw).is_file() else json.loads(raw)
    )
    return service_account.Credentials.from_service_account_info(
        key_data, scopes=_DRIVE_SCOPES
    )


class GoogleDriveService:
    """Folder CRUD / upload / share."""

    def __init__(self, creds: Credentials | None = None) -> None:
        creds = creds or _default_creds()
        self._svc = build("drive", "v3", credentials=creds, cache_discovery=False)
        self._files = self._svc.files()
        self._permissions = self._svc.permissions()

    # ─────────────────────────── folders ────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def create_folder(self, name: str, parent_id: str | None = None) -> dict[str, str]:
        body: dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            body["parents"] = [parent_id]
        return self._files.create(body=body, fields="id,name,parents").execute()

    # ─────────────────────────── uploads ────────────────────────────

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

    # ─────────────────────────── sharing ────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def share_folder(
        self,
        folder_id: str,
        email: str,
        role: str = "writer",  # one of: reader | writer | commenter
    ) -> dict[str, str]:
        body = {"type": "user", "role": role, "emailAddress": email}
        return self._permissions.create(
            fileId=folder_id,
            sendNotificationEmail=False,
            body=body,
            fields="id,emailAddress,role",
        ).execute()
