import sqlalchemy as sa
from app.core.models.base import Base

class Organisation(Base):
    __tablename__ = "organisations"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(128), nullable=False, unique=True)
    workspace_folder_id = sa.Column(sa.String(128), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), onupdate=sa.func.now())

__all__ = ["Organisation"]
