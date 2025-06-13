from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.extensions import db
from app.core.models.base import BaseModel

class Status(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"

class WootPorf(BaseModel):
    __tablename__ = "woot_porfs"

    porf_no = Column(String, unique=True, nullable=False)
    status  = Column(SQLEnum(Status), default=Status.DRAFT)
    lines   = relationship("WootPorfLine", back_populates="porf")

class WootPorfLine(BaseModel):
    __tablename__ = "woot_porf_lines"

    porf_id    = Column(Integer, ForeignKey("woot_porfs.id"), nullable=False)
    product_id = Column(String, nullable=False)
    quantity   = Column(Integer, nullable=False)
    porf       = relationship("WootPorf", back_populates="lines")
