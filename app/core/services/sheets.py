from __future__ import annotations

from typing import Any, List, Tuple, Dict

from app.core.services.google.sheets import GoogleSheetsService


class SheetsService(GoogleSheetsService):
    """Application-level convenience wrapper around Google Sheets."""

    def __init__(self, credentials=None) -> None:
        if credentials is None:
            self.service = None
            self.spreadsheets = None
        else:
            super().__init__(credentials)

    def open_sheet(self, sheet_id: str) -> Dict[str, Any]:
        """Return spreadsheet metadata."""
        return self.spreadsheets.get(spreadsheetId=sheet_id).execute()

    def copy_template(self, src_id: str, dst_title: str, folder_id: str) -> Tuple[str, str]:
        """Copy ``src_id`` to ``dst_title`` inside ``folder_id``."""
        body = {"name": dst_title, "parents": [folder_id]}
        copy = self.service.files().copy(fileId=src_id, body=body).execute()
        sheet_id = copy["id"]
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
        return sheet_id, url

    def append_rows(
        self, spreadsheet_id: str, rows: List[List[Any]], range_name: str = "Sheet1!A1"
    ) -> Dict[str, Any]:
        """Append ``rows`` to ``spreadsheet_id``."""
        return super().append_rows(spreadsheet_id, rows, range_name)
