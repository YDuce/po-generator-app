# pylint: disable=too-few-public-methods
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from database import Base


class InventoryRecord(Base):
    """Time-stamped delta in on-hand units for a *product* on a *channel*."""

    __tablename__ = "inventory_record"

    id = Column(Integer, primary_key=True)

    # Foreign keys
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channel.id"), nullable=False)

    # Delta (+/-) from the previous snapshot
    delta = Column(Integer, nullable=False)

    source = Column(String, nullable=True)
    recorded_at = Column(DateTime, server_default=func.now(), nullable=False) 