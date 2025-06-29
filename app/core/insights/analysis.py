from datetime import datetime, timedelta
from logging import getLogger
from typing import List

from sqlalchemy.orm import Session

from app.core.models.product import MasterProduct, InventoryRecord

logger = getLogger(__name__)


class InventoryInsights:
    """Simple analytics on product movement."""

    def __init__(self, db: Session):
        self.db = db

    def slow_movers(self, days: int = 60) -> List[MasterProduct]:
        """Return products with no inventory movement in ``days`` days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        subq = (
            self.db.query(InventoryRecord.product_id)
            .filter(InventoryRecord.created_at >= cutoff)
            .subquery()
        )
        products = self.db.query(MasterProduct).filter(~MasterProduct.id.in_(subq)).all()
        logger.debug("%d slow movers found", len(products))
        return products
