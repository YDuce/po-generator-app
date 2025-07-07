"""Google Sheets management."""

from typing import Any

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from typing import cast
import redis
from inventory_manager_app.core.config.settings import get_settings


class SheetsService:
    """Wrapper around the Google Sheets API."""

    def __init__(
        self, creds: Credentials, redis_client: redis.Redis | None = None
    ) -> None:
        self.client = build(
            "sheets",
            "v4",
            credentials=creds,
            cache_discovery=False,
        )
        self.redis = redis_client or redis.Redis.from_url(
            get_settings().redis_url
        )

    def create_spreadsheet(self, name: str) -> dict[str, Any]:
        spreadsheet = {"properties": {"title": name}}
        with self.redis.lock("gapi", timeout=10, blocking_timeout=10):
            resp = (
                self.client.spreadsheets()
                .create(body=spreadsheet, fields="spreadsheetId")
                .execute()
            )
        return cast(dict[str, Any], resp)

    def append_row(
        self, spreadsheet_id: str, range_: str, values: list[Any]
    ) -> dict[str, Any]:
        body = {"values": [values]}
        resp = None
        with self.redis.lock("gapi", timeout=10, blocking_timeout=10):
            resp = (
                self.client.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
        return cast(dict[str, Any], resp)
