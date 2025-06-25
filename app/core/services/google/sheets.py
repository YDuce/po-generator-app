"""Google Sheets helper (read / append / update / copy template)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from flask import current_app, has_app_context
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential

_SHEETS_SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets"]


def _load_creds_from_env() -> Credentials:
    raw = os.getenv("GOOGLE_SVC_KEY")
    if not raw:
        raise RuntimeError("Google service-account key not supplied")
    data = json.loads(Path(raw).read_text()) if Path(raw).is_file() else json.loads(raw)
    return service_account.Credentials.from_service_account_info(data, scopes=_SHEETS_SCOPES)


def _default_creds() -> Credentials:
    if has_app_context():
        cfg_creds: Credentials | None = current_app.config.get("GOOGLE_SVC_CREDS")  # type: ignore[arg-type]
        if cfg_creds is not None:
            return cfg_creds
    return _load_creds_from_env()


class SheetResponse(TypedDict):
    spreadsheetId: str
    updatedRange: str
    updatedRows: int
    updatedColumns: int
    updatedCells: int


class GoogleSheetsService:
    """Sheets v4 wrapper.  Mutations can be disabled at construction time."""

    def __init__(
        self,
        creds: Credentials | None = None,
        *,
        mutations_allowed: bool = True,
    ) -> None:
        self._creds = creds or _default_creds()
        self._svc = build("sheets", "v4", credentials=self._creds, cache_discovery=False)
        self._spreadsheets = self._svc.spreadsheets()
        self._mutations_allowed = mutations_allowed

    # ───────────────────── reads ──────────────────────
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def get_values(self, sheet_id: str, rng: str) -> List[List[str]]:
        resp = self._spreadsheets.values().get(spreadsheetId=sheet_id, range=rng).execute()
        return resp.get("values", [])

    # ───────────────────── writes ─────────────────────
    def _guard(self) -> None:
        if not self._mutations_allowed:
            raise RuntimeError("Two-way Sheets sync disabled")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def update_values(
        self,
        sheet_id: str,
        rng: str,
        rows: List[List[Any]],
    ) -> SheetResponse:  # type: ignore[override]
        self._guard()
        body = {"values": rows}
        return self._spreadsheets.values().update(
            spreadsheetId=sheet_id,
            range=rng,
            valueInputOption="RAW",
            body=body,
        ).execute()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def append_values(
        self,
        sheet_id: str,
        rng: str,
        rows: List[List[Any]],
    ) -> SheetResponse:  # type: ignore[override]
        self._guard()
        body = {"values": rows}
        return self._spreadsheets.values().append(
            spreadsheetId=sheet_id,
            range=rng,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    # ─────── copy template into Drive folder & return (id, link) ───────
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=10))
    def copy_template(
        self,
        template_id: str,
        new_title: str,
        dst_folder: str,
    ) -> tuple[str, str]:
        drive = build("drive", "v3", credentials=self._creds, cache_discovery=False)
        body: Dict[str, Any] = {"name": new_title, "parents": [dst_folder]}
        new_file = drive.files().copy(
            fileId=template_id,
            body=body,
            fields="id,webViewLink",
        ).execute()
        return new_file["id"], new_file["webViewLink"]