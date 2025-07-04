from datetime import datetime, timedelta


def test_generate_insights_creates_reallocation(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_SECRET_KEY", "test-secret")
    from inventory_manager_app.core.config.settings import settings
    from inventory_manager_app import create_app, db
    from inventory_manager_app.core.models import Product
    from inventory_manager_app.tests.utils import migrate_database
    from inventory_manager_app.core.services.insights import InsightsService

    monkeypatch.setattr(
        settings, "database_url", f"sqlite:///{str(tmp_path / 'test.db')}"
    )
    app = create_app()
    migrate_database(app)
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
