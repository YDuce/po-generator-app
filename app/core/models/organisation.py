"""Organisation model storing workspace info.

Layer: core
"""

from sqlalchemy import Column, String
from app.core.models.base import BaseModel


class Organisation(BaseModel):
    """Organisation row."""

    __tablename__ = "organisations"

    name = Column(String(100), unique=True, nullable=False)
    workspace_folder_id = Column(String(255), nullable=True)
