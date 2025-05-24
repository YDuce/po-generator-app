from sqlalchemy import Column, Integer, String
from .base import Base

class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False) 