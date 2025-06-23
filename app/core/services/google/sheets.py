from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, TypedDict

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential

_SHEETS_SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]

def _default_creds() -> Credentials:
    raw = os.getenv("GOOGLE_SVC_KEY")
    if raw is None:
        raise RuntimeError("Google Sheets credentials not supplied")
    key_data = (
        json.loads(Path(raw).read_text()) if Path(raw).is_file() else json.loads(raw)
    )
    return service_account.Credentials.from_service_account_info(
        key_data, scopes=_SHEETS_SCOPES
    )

class SheetResponse(TypedDict):
    spreadsheetId: str
    updatedRange: str
    updatedRows: int
    updatedColumns: int
    updatedCells: int

class GoogleSheetsService:
    """Light-weight Sheets helper with optional write protection."""

    def __init__(self, creds: Credentials | None = None, *, mutations_allowed: bool = True) -> None:
        creds = creds or _default_creds()
        self._creds = creds
        self._svc = build("sheets", "v4", credentials=creds, cache_discovery=False)
        self._spreadsheets = self._svc.spreadsheets()
        self._mutations_allowed = mutations_allowed

    # ---------------------------------------------------------------- read

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def get_values(self, sheet_id: str, rng: str) -> list[list[str]]:
        resp = (
            self._spreadsheets.values()
            .get(spreadsheetId=sheet_id, range=rng)
            .execute()
        )
        return resp.get("values", [])

    # ---------------------------------------------------------------- write

    def _guard(self) -> None:
        if not self._mutations_allowed:
            raise RuntimeError("Two-way Sheets sync disabled")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def update_values(
        self,
        sheet_id: str,
        rng: str,
        rows: list[list[Any]],
    ) -> SheetResponse:  # type: ignore[override]
        self._guard()
        body = {"values": rows}
        return (
            self._spreadsheets.values()
            .update(
                spreadsheetId=sheet_id,
                range=rng,
                valueInputOption="RAW",
                body=body,
            )
            .execute()
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def append_values(
        self,
        sheet_id: str,
        rng: str,
        rows: list[list[Any]],
    ) -> SheetResponse:  # type: ignore[override]
        self._guard()
        body = {"values": rows}
        return (
            self._spreadsheets.values()
            .append(
                spreadsheetId=sheet_id,
                range=rng,
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )

    # ---------------------------------------------------------------- template copy

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def copy_template(
        self,
        template_id: str,
        new_title: str,
        dst_folder: str,
    ) -> tuple[str, str]:
        drive = build(
            "drive", "v3", credentials=self._creds, cache_discovery=False
        )
        body: dict[str, Any] = {"name": new_title, "parents": [dst_folder]}
        new_file = (
            drive.files()
            .copy(
                fileId=template_id,
                body=body,
                fields="id,webViewLink",
            )
            .execute()
        )
        return new_file["id"], new_file["webViewLink"]