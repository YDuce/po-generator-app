from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class PO(Base):
    """Purchase Order associated with a PORF."""

    __tablename__ = "po"

    id = Column(Integer, primary_key=True)
    po_no = Column(String, unique=True, nullable=False)
    porf_id = Column(Integer, ForeignKey("porf.id"), nullable=False)
    pdf_path = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=False, server_default=func.now()) 