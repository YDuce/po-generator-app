"""Google Sheets management."""

from typing import Any

from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


class SheetsService:
    """Wrapper around the Google Sheets API."""

    def __init__(self, creds: Credentials) -> None:
        self.client = build("sheets", "v4", credentials=creds, cache_discovery=False)

    def create_spreadsheet(self, name: str) -> dict[str, Any]:
        spreadsheet = {"properties": {"title": name}}
        return (
            self.client.spreadsheets()
            .create(body=spreadsheet, fields="spreadsheetId")
            .execute()
        )
