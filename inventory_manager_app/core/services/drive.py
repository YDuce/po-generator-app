"""Google Drive management."""

from typing import Any, cast

import redis
from inventory_manager_app.core.config.settings import get_settings

from googleapiclient.discovery import build

from google.oauth2.service_account import Credentials


class DriveService:
    """Wrapper around the Google Drive API."""

    def __init__(
        self, creds: Credentials, redis_client: redis.Redis | None = None
    ) -> None:
        self.client = build(
            "drive",
            "v3",
            credentials=creds,
            cache_discovery=False,
        )
        self.redis = cast(
            redis.Redis,
            redis_client or redis.Redis.from_url(get_settings().redis_url),
        )

    def create_folder(self, name: str, parent_id: str | None = None) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_id:
            metadata["parents"] = [parent_id]
        with self.redis.lock("gapi", timeout=10, blocking_timeout=10):
            resp = self.client.files().create(body=metadata, fields="id").execute()
        return cast(dict[str, Any], resp)
