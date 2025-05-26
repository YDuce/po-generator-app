from sqlalchemy import Column, Integer, ForeignKey
from models.base import JSONB
from database import Base

class PORFLine(Base):
    """Line item within a PORF."""

    __tablename__ = "porf_line"

    id = Column(Integer, primary_key=True)
    porf_id = Column(Integer, ForeignKey("porf.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    qty = Column(Integer, nullable=False)
    extra = Column(JSONB, nullable=True)  # arbitrary JSON (cost, notes) 