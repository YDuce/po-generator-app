from __future__ import annotations

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from .base import BaseModel

class Organisation(BaseModel):
    """
    Tenant / company boundary.

    We keep only length checks here because SQLite **does not** support the
    PostgreSQL '~' regex operator that was in the earlier constraint.
    """
    __tablename__ = "organisations"
    __table_args__ = (
        CheckConstraint("length(drive_folder_id) >= 25", name="ck_org_drive_id_min"),
        CheckConstraint("length(drive_folder_id) <= 256", name="ck_org_drive_id_max"),
    )

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    drive_folder_id: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organisation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organisation {self.name}>"