from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Insight(Base):
    __tablename__ = 'insight'

    product_sku: Mapped[str] = mapped_column(ForeignKey('product.sku'), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    generated_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    product: Mapped['Product'] = relationship(back_populates='insights')
