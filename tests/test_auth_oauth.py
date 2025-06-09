import types
from app.core.auth.models import User


def test_google_oauth_flow(client, db_session, monkeypatch):
    class FakeResp:
        def json(self):
            return {"id": "gid", "email": "test@example.com", "name": "Tester"}

    google_mod = types.SimpleNamespace(authorized=True, get=lambda url: FakeResp())
    monkeypatch.setattr("app.api.auth.google", google_mod)

    resp = client.get("/api/auth/login/google")
    assert resp.status_code == 200
    assert "token" in resp.json
    session = db_session()
    assert session.query(User).filter_by(email="test@example.com").count() == 1
