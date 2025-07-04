"""Insights generation logic."""

from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from ..models import Insight, Product, Reallocation

logger = logging.getLogger(__name__)


class InsightsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate(self, threshold_days: int = 30) -> list[Insight]:
        now = datetime.utcnow()
        cutoff = now - timedelta(days=threshold_days)
        insights: list[Insight] = []
        products = self.db.query(Product).order_by(Product.id).yield_per(100)
        for product in products:
            status = None
            if product.quantity == 0:
                status = "out-of-stock"
            elif product.listed_date < cutoff:
                status = "slow-mover"
            if status:
                insight = Insight(
                    product_sku=product.sku,
                    channel=product.channel,
                    status=status,
                    generated_date=now,
                )
                self.db.add(insight)
                insights.append(insight)
                stmt = insert(Reallocation).values(
                    sku=product.sku,
                    channel_origin=product.channel,
                    reason=status,
                    added_date=now,
                )
                dialect = self.db.get_bind().dialect.name
                if dialect == "sqlite":
                    stmt = stmt.prefix_with("OR IGNORE")
                    self.db.execute(stmt)
                elif dialect == "postgresql":
                    stmt = stmt.on_conflict_do_nothing(
                        index_elements=["sku", "channel_origin", "reason"]
                    )
                    self.db.execute(stmt)
                else:
                    try:
                        self.db.execute(stmt)
                    except IntegrityError:
                        self.db.rollback()
                        logger.debug(
                            "Duplicate reallocation for %s/%s",
                            product.sku,
                            product.channel,
                        )
        if insights:
            self.db.commit()
        return insights
