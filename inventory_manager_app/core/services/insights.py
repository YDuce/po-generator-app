"""Insights generation logic."""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..models import Insight, Product


class InsightsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate(self, threshold_days: int = 30) -> list[Insight]:
        now = datetime.utcnow()
        cutoff = now - timedelta(days=threshold_days)
        insights: list[Insight] = []
        products = self.db.query(Product).all()
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
        if insights:
            self.db.commit()
        return insights
