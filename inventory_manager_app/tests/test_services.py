import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any

from inventory_manager_app.channels.amazon.actions import AmazonActions
from inventory_manager_app.channels.amazon.tasks import AmazonTasks
from inventory_manager_app.channels.amazon.utils import helper as amazon_helper
from inventory_manager_app.channels.ebay.actions import EbayActions
from inventory_manager_app.channels.ebay.tasks import EbayTasks
from inventory_manager_app.channels.ebay.utils import helper as ebay_helper
from inventory_manager_app.channels.woot.actions import WootActions
from inventory_manager_app.channels.woot.tasks import WootTasks
from inventory_manager_app.channels.woot.utils import helper as woot_helper
from inventory_manager_app.core.services import (
    DriveService,
    SheetsService,
    WebhookService,
)


class DummyCaller:
    def __init__(self):
        self.called = False
        self.args = None

    def execute(self):
        self.called = True
        return {"id": "123", "spreadsheetId": "SID"}

    def create(self, body=None, fields=None):
        self.args = (body, fields)
        return self

    def files(self):
        return self

    def spreadsheets(self):
        return self


class DummySheets:
    def __init__(self) -> None:
        self.called = False
        self.args = None

    def append_row(self, spreadsheet_id: str, range_: str, values: list[str]) -> None:
        self.called = True
        self.args = (spreadsheet_id, range_, values)


class FakeRedis:
    def __init__(self) -> None:
        self.store: dict[str, str] = {}

    class _Lock:
        def __enter__(self, *args) -> None:
            return None

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    def get(self, key: str) -> str | None:
        return self.store.get(key)

    def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.store[key] = value

    def lock(
        self,
        name: str,
        timeout: int | None = None,
        blocking_timeout: int | None = None,
    ):
        return self._Lock()

    def incr(self, key: str) -> int:
        val = int(self.store.get(key, "0")) + 1
        self.store[key] = str(val)
        return val

    def expire(self, key: str, seconds: int) -> None:
        pass


def test_drive_and_sheets(monkeypatch):
    dummy = DummyCaller()

    def fake_build(service, version, credentials=None, cache_discovery=False):
        return dummy

    monkeypatch.setattr("inventory_manager_app.core.services.drive.build", fake_build)
    monkeypatch.setattr("inventory_manager_app.core.services.sheets.build", fake_build)
    drive = DriveService(creds=object(), redis_client=FakeRedis())
    res = drive.create_folder("Test", parent_id="PID")
    assert dummy.called
    assert dummy.args[0]["name"] == "Test"
    assert dummy.args[0]["parents"] == ["PID"]
    assert res == {"id": "123", "spreadsheetId": "SID"}

    dummy.called = False
    sheets = SheetsService(creds=object(), redis_client=FakeRedis())
    res2 = sheets.create_spreadsheet("Book")
    assert dummy.called
    assert res2 == {"id": "123", "spreadsheetId": "SID"}


def test_webhook_verify(monkeypatch):
    service = WebhookService(["s"], FakeRedis(), object())
    payload = b"data"
    sig = hmac.new(b"s", payload, hashlib.sha256).hexdigest()
    assert service.verify(payload, sig)
    assert not service.verify(payload, sig)
    assert not service.verify(payload, "bad")


def test_channel_helpers():
    AmazonActions.log_event({"x": 1})
    AmazonTasks.process_event({"y": 2})
    amazon_helper("msg")
    EbayActions.log_event({"x": 1})
    EbayTasks.process_event({"y": 2})
    ebay_helper("m")
    WootActions.handle_porfs({"z": 3})
    WootTasks.process_event({"w": 4})
    woot_helper("m2")


def _webhook_payload(qty: int = 1) -> tuple[bytes, dict[str, Any], str]:
    import json

    body = {
        "order_id": "OID1",
        "channel": "amazon",
        "product_sku": "SKU1",
        "quantity": qty,
    }
    raw = json.dumps(body).encode()
    sig = hmac.new(b"secret", raw, hashlib.sha256).hexdigest()
    return raw, body, sig


def test_webhook_process_success(tmp_path, monkeypatch):
    from inventory_manager_app.core.models import OrderRecord
    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)
    dummy = DummySheets()

    with app.app_context():
        from inventory_manager_app.core.models import ChannelSheet, Organisation
        from inventory_manager_app.extensions import db

        org = Organisation(name="Org", drive_folder_id="1")
        db.session.add(org)
        db.session.commit()
        db.session.add(
            ChannelSheet(
                organisation_id=org.id,
                channel="amazon",
                folder_id="FID",
                spreadsheet_id="SID",
            )
        )
        from inventory_manager_app.core.models import Product
        db.session.add(Product(sku="SKU1", name="P", channel="amazon"))
        db.session.commit()

        service = WebhookService(["secret"], FakeRedis(), db.session)
        payload, body, sig = _webhook_payload()
        msg, code = service.process(payload, sig, body, dummy, "rid")
        assert code == 204
        assert OrderRecord.query.filter_by(order_id="OID1").count() == 1
        from inventory_manager_app.core.models import Insight
        assert Insight.query.filter_by(product_sku="SKU1").count() == 1
        assert dummy.called

    app.teardown_db()


def test_webhook_process_bad_signature(tmp_path, monkeypatch):
    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)

    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(["secret"], FakeRedis(), db.session)
        payload, body, _ = _webhook_payload()
        msg, code = service.process(payload, "bad", body, request_id="rid")
        assert code == 403

    app.teardown_db()


def test_webhook_process_replay(tmp_path, monkeypatch):
    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)

    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(
            ["secret"], FakeRedis(), db.session, window_seconds=300
        )
        payload, body, sig = _webhook_payload()
        service.process(payload, sig, body, request_id="rid")
        msg, code = service.process(payload, sig, body, request_id="rid")
        assert code == 403

    app.teardown_db()


def test_webhook_process_malformed(tmp_path, monkeypatch):
    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)

    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(["secret"], FakeRedis(), db.session)
        payload = b"{}"
        sig = hmac.new(b"secret", payload, hashlib.sha256).hexdigest()
        msg, code = service.process(payload, sig, {}, request_id="rid")
        assert code == 400

    app.teardown_db()


def test_webhook_process_upsert(tmp_path, monkeypatch):
    from inventory_manager_app.core.models import OrderRecord
    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)

    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(["secret"], FakeRedis(), db.session)
        p1, b1, s1 = _webhook_payload(1)
        service.process(p1, s1, b1, request_id="rid")
        p2, b2, s2 = _webhook_payload(5)
        service.process(p2, s2, b2, request_id="rid")
        order = OrderRecord.query.filter_by(order_id="OID1").first()
        assert order and order.quantity == 5

    app.teardown_db()


def test_webhook_process_sheet_error(tmp_path, monkeypatch):
    from inventory_manager_app.tests.utils import create_test_app

    class FailingSheets(DummySheets):
        def append_row(self, *a, **kw):
            super().append_row(*a, **kw)
            raise RuntimeError("boom")

    app = create_test_app(tmp_path, monkeypatch)
    dummy = FailingSheets()

    with app.app_context():
        from inventory_manager_app.core.models import ChannelSheet, Organisation
        from inventory_manager_app.extensions import db

        org = Organisation(name="Org", drive_folder_id="1")
        db.session.add(org)
        db.session.commit()
        db.session.add(
            ChannelSheet(
                organisation_id=org.id,
                channel="amazon",
                folder_id="FID",
                spreadsheet_id="SID",
            )
        )
        db.session.commit()

        service = WebhookService(["secret"], FakeRedis(), db.session)
        payload, body, sig = _webhook_payload()
        msg, code = service.process(payload, sig, body, dummy, "rid")
        assert code == 204
        assert dummy.called

    app.teardown_db()


def test_webhook_missing_channel(tmp_path, monkeypatch):
    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)

    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(["secret"], FakeRedis(), db.session)
        payload, body, sig = _webhook_payload()
        msg, code = service.process(payload, sig, body, DummySheets(), "rid")
        assert code == 400

    app.teardown_db()


def test_webhook_rotate_secrets(tmp_path, monkeypatch):
    import tempfile

    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)

    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(["old"], FakeRedis(), db.session)
        payload, body, sig = _webhook_payload()
        msg, code = service.process(payload, sig, body, request_id="rid")
        assert code == 403

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(b"secret\n")
        tmp.close()
        service.rotate_from_file(tmp.name)
        payload, body, sig = _webhook_payload()
        msg, code = service.process(payload, sig, body, request_id="rid")
        assert code == 204

    app.teardown_db()


def test_settings_load_secrets_file(tmp_path, monkeypatch):
    from inventory_manager_app.core.config.settings import get_settings

    path = tmp_path / "secrets.txt"
    path.write_text("a\nb\n")
    monkeypatch.setenv("APP_SECRET_KEY", "x")
    monkeypatch.setenv("APP_WEBHOOK_SECRETS_FILE", str(path))
    sa_file = tmp_path / "sa.json"
    sa_file.write_text("{}")
    monkeypatch.setenv("APP_SERVICE_ACCOUNT_FILE", str(sa_file))
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.webhook_secrets == ["a", "b"]


def test_webhook_rate_limit(tmp_path, monkeypatch):
    import inventory_manager_app.core.webhooks.shipstation as ship
    from inventory_manager_app.tests.utils import create_test_app

    app = create_test_app(tmp_path, monkeypatch)
    fake = FakeRedis()
    fixed_time = datetime(2023, 1, 1, tzinfo=timezone.utc)

    class _FixedDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed_time

    monkeypatch.setattr(ship, "datetime", _FixedDatetime)
    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(["secret"], fake, db.session)
        monkeypatch.setattr(service, "process", lambda *a, **k: ("", 204))

    monkeypatch.setattr(ship, "_service", lambda: (service, DummySheets(), fake))

    with app.test_client() as client:
        for _ in range(100):
            client.post(
                "/api/v1/webhook/shipstation",
                data=b"{}",
                headers={"Content-Type": "application/json"},
            )
        resp = client.post(
            "/api/v1/webhook/shipstation",
            data=b"{}",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 429
        assert resp.get_json()["error"] == "Too many requests"
    app.teardown_db()


def test_webhook_payload_limit(tmp_path, monkeypatch):
    import inventory_manager_app.core.webhooks.shipstation as ship
    from inventory_manager_app.tests.utils import create_test_app
    from inventory_manager_app.core.config.settings import get_settings

    app = create_test_app(tmp_path, monkeypatch)
    fake = FakeRedis()

    with app.app_context():
        from inventory_manager_app.extensions import db

        service = WebhookService(["secret"], fake, db.session)
        monkeypatch.setattr(service, "process", lambda *a, **k: ("", 204))

    monkeypatch.setattr(ship, "_service", lambda: (service, DummySheets(), fake))

    with app.test_client() as client:
        size = get_settings().max_payload + 1
        resp = client.post(
            "/api/v1/webhook/shipstation",
            data=b"x" * size,
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 413
        assert resp.get_json()["error"] == "Payload too large"

    app.teardown_db()
