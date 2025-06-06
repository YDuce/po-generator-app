import io


def test_porf_upload(client):
    # Create dummy XLSX content (empty) as bytes (required minimal openpyxl file) – use simple CSV.
    dummy = b"dummy-content"
    data = {
        "file": (io.BytesIO(dummy), "test.xlsx"),
    }
    resp = client.post(
        "/api/porf/upload", data=data, content_type="multipart/form-data"
    )
    assert resp.status_code == 201
    assert "porf_id" in resp.json
