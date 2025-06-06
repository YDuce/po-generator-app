from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base


class PORF(Base):
    """Purchase Order Request Form (PORF)."""

    __tablename__ = "porf"

    id = Column(Integer, primary_key=True)
    porf_no = Column(String, unique=True, nullable=False)
    status = Column(String, default="draft", nullable=False)  # draft/approved/expired
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
