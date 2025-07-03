from __future__ import annotations

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Product(Base):
    __tablename__ = 'product'

    sku: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(50), default='active')
    listed_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    orders: Mapped[list['OrderRecord']] = relationship(back_populates='product')
    insights: Mapped[list['Insight']] = relationship(back_populates='product')
