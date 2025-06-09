import io
from app.core.services.drive import DriveService
from app.core.services.sheets import SheetsService
import types

def test_porf_upload(client, monkeypatch) -> None:
    # Patch DriveService and SheetsService to avoid real Google API calls
    monkeypatch.setattr(DriveService, "__init__", lambda self, creds: None)
    monkeypatch.setattr(SheetsService, "__init__", lambda self, creds: None)
    monkeypatch.setattr("app.channels.woot.routes.ingest_porf", lambda file, drive, sheets: {"porf_id": 1})

    # Create dummy XLSX content (empty) as bytes (required minimal openpyxl file) – use simple CSV.
    dummy = b"dummy-content"
    data = {
        "file": (io.BytesIO(dummy), "test.xlsx"),
    }
    resp = client.post(
        "/api/woot/porf-upload", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 201
    assert "porf_id" in resp.json
