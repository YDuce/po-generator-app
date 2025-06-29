from app.core.insights.reallocation import ReallocationService
from app.core.models import MasterProduct
from app.extensions import db


def test_add_and_list_candidates(app) -> None:
    with app.app_context():
        prod = MasterProduct(sku="SKU1", title="Test")
        db.session.add(prod)
        db.session.commit()

        svc = ReallocationService(db.session)
        cand = svc.add_candidate(prod, from_channel="woot", reason="slow")
        db.session.commit()

        rows = svc.all_candidates()
        assert len(rows) == 1
        assert rows[0].id == cand.id
        assert rows[0].from_channel == "woot"
