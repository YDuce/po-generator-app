"""Tests for organisation API endpoints."""

from __future__ import annotations

import os
import pytest

from inventory_manager_app.tests.utils import create_test_app, create_token_for


pytestmark = pytest.mark.skipif(
    "POSTGRES_URL" not in os.environ,
    reason="Postgres not available",
)


def test_create_and_list_org(tmp_path, monkeypatch):
    app = create_test_app(tmp_path, monkeypatch)
    token = create_token_for(app)
    headers = {"Authorization": f"Bearer {token}"}
    with app.test_client() as client:
        resp = client.post(
            "/api/v1/organisations",
            json={"name": "Acme", "drive_folder_id": "ABC123"},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.headers.get("Location", "").endswith("/api/v1/organisations")
        org_id = resp.get_json()["id"]

        resp = client.get("/api/v1/organisations", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert any(o["id"] == org_id for o in data)


def test_org_auth_required(tmp_path, monkeypatch):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import User
    from inventory_manager_app.core.utils.auth import hash_password, create_token
    from inventory_manager_app.core.config.settings import settings

    app = create_test_app(tmp_path, monkeypatch)
    with app.test_client() as client:
        assert client.get("/api/v1/organisations").status_code == 401

    with app.app_context():
        user = User(
            email="user@example.com",
            organisation_id=1,
            password_hash=hash_password("x"),
            allowed_channels=[],
        )
        db.session.add(user)
        db.session.commit()
        token = create_token({"sub": user.id}, settings.secret_key)

    headers = {"Authorization": f"Bearer {token}"}
    with app.test_client() as client:
        assert client.get("/api/v1/organisations", headers=headers).status_code == 403


def test_org_duplicate(tmp_path, monkeypatch):
    app = create_test_app(tmp_path, monkeypatch)
    token = create_token_for(app)
    headers = {"Authorization": f"Bearer {token}"}
    with app.test_client() as client:
        assert (
            client.post(
                "/api/v1/organisations",
                json={"name": "Acme", "drive_folder_id": "ABC123"},
                headers=headers,
            ).status_code
            == 201
        )
        resp = client.post(
            "/api/v1/organisations",
            json={"name": "Acme", "drive_folder_id": "ABC123"},
            headers=headers,
        )
        assert resp.status_code == 409
