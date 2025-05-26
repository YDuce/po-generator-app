from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class SalesOrder(Base):
    """Represents a sales order event from a channel."""

    __tablename__ = "sales_order"

    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channel.id"), nullable=False)
    external_id = Column(String, unique=True, nullable=False)
    placed_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)

    order_lines = relationship("OrderLine", back_populates="sales_order") 