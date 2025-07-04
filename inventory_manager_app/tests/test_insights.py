from datetime import datetime, timedelta

import os
import pytest

from inventory_manager_app.tests.utils import create_test_app


pytestmark = pytest.mark.skipif(
    "POSTGRES_URL" not in os.environ,
    reason="Postgres not available",
)


def test_generate_insights_creates_reallocation(tmp_path, monkeypatch):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import Product
    from inventory_manager_app.core.services.insights import InsightsService

    app = create_test_app(tmp_path, monkeypatch)
    with app.app_context():
        prod = Product(
            sku="ABC",
            name="Test",
            channel="amazon",
            quantity=0,
            listed_date=datetime.utcnow() - timedelta(days=40),
        )
        db.session.add(prod)
        db.session.commit()
        service = InsightsService(db.session)
        insights = service.generate(threshold_days=30)
        assert insights
        from inventory_manager_app.core.models import Reallocation

        realloc = Reallocation.query.filter_by(
            sku="ABC", channel_origin="amazon"
        ).first()
        assert realloc is not None


def test_generate_insights_slow_mover(tmp_path, monkeypatch):
    from inventory_manager_app import db
    from inventory_manager_app.core.models import Product
    from inventory_manager_app.core.services.insights import InsightsService

    app = create_test_app(tmp_path, monkeypatch)
    with app.app_context():
        prod = Product(
            sku="SLOW",
            name="Slow Prod",
            channel="woot",
            quantity=5,
            listed_date=datetime.utcnow() - timedelta(days=40),
        )
        db.session.add(prod)
        db.session.commit()
        service = InsightsService(db.session)
        insights = service.generate(threshold_days=30)
        assert any(i.product_sku == "SLOW" for i in insights)
