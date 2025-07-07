import hmac
import hashlib

from inventory_manager_app.core.services.drive import DriveService
from inventory_manager_app.core.services.sheets import SheetsService
from inventory_manager_app.core.services.webhook import WebhookService
from inventory_manager_app.channels.amazon.actions import AmazonActions
from inventory_manager_app.channels.amazon.tasks import AmazonTasks
from inventory_manager_app.channels.amazon.utils import helper as amazon_helper
from inventory_manager_app.channels.ebay.actions import EbayActions
from inventory_manager_app.channels.ebay.tasks import EbayTasks
from inventory_manager_app.channels.ebay.utils import helper as ebay_helper
from inventory_manager_app.channels.woot.actions import WootActions
from inventory_manager_app.channels.woot.tasks import WootTasks
from inventory_manager_app.channels.woot.utils import helper as woot_helper


class DummyCaller:
    def __init__(self):
        self.called = False
        self.args = None

    def execute(self):
        self.called = True
        return {"id": "123"}

    def create(self, body=None, fields=None):
        self.args = (body, fields)
        return self

    def files(self):
        return self

    def spreadsheets(self):
        return self


def test_drive_and_sheets(monkeypatch):
    dummy = DummyCaller()

    def fake_build(service, version, credentials=None, cache_discovery=False):
        return dummy

    monkeypatch.setattr("inventory_manager_app.core.services.drive.build", fake_build)
    monkeypatch.setattr("inventory_manager_app.core.services.sheets.build", fake_build)
    drive = DriveService(creds=object())
    res = drive.create_folder("Test", parent_id="PID")
    assert dummy.called
    assert dummy.args[0]["name"] == "Test"
    assert dummy.args[0]["parents"] == ["PID"]
    assert res == {"id": "123"}

    dummy.called = False
    sheets = SheetsService(creds=object())
    res2 = sheets.create_spreadsheet("Book")
    assert dummy.called
    assert res2 == {"id": "123"}


def test_webhook_verify(monkeypatch):
    service = WebhookService(["s"])
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
