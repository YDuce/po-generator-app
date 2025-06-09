import io
from unittest import mock
from app.channels.woot.models import WootPorf
from sqlalchemy import select, func


def test_porf_upload(client, db_session, monkeypatch):
    dummy = b"dummy-content"
    data = {
        "file": (io.BytesIO(dummy), "test.xlsx"),
    }
    called = {}

    def fake_copy(src_id: str, title: str, folder: str):
        called["title"] = title
        return "sid", "url"

    monkeypatch.setattr(
        "app.core.services.sheets.SheetsService.copy_template",
        fake_copy,
    )

    resp = client.post(
        "/api/porf/upload", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 201
    assert "porf_id" in resp.json
    assert called["title"].startswith("porf-")
    session = db_session()
    count = session.execute(select(func.count()).select_from(WootPorf)).scalar_one()
    assert count == 1
