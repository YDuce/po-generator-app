from datetime import datetime, timezone

import pytest

from app.channels import ChannelAdapter, Channel
from app.extensions import db
from app.tasks.sync import _sync_user
from app.core.models import Organisation, User, MasterProduct, OrderRecord, OrderStatus


class FakeAdapter(ChannelAdapter):
    def fetch_orders(self):
        from app.core.logic.orders import OrderLinePayload, OrderPayload

        yield OrderPayload(
            ext_id="X1",
            channel=Channel.WOOT,
            placed_at=datetime.now(timezone.utc),
            status=OrderStatus.NEW,
            currency="USD",
            total="5.00",
            lines=[OrderLinePayload(sku="SKU1", quantity=1, unit_price="5.00")],
        )


@pytest.mark.usefixtures("app")
def test_sync_task_inserts_orders(app, monkeypatch):
    monkeypatch.setattr("app.tasks.sync.get_adapter", lambda name: FakeAdapter())

    with app.app_context():
        org = Organisation(name="Org", drive_folder_id="F" * 25 + "2")
        db.session.add(org)
        prod = MasterProduct(sku="SKU1", title="Item")
        db.session.add(prod)
        user = User(email="t@example.com", organisation=org, allowed_channels=["woot"])
        db.session.add(user)
        db.session.commit()

        count = _sync_user(user)
        db.session.commit()

        assert count == 1
        assert db.session.query(OrderRecord).count() == 1
