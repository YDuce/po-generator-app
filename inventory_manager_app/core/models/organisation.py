from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

from .base import Base


class Organisation(Base):
    __tablename__ = "organisation"  # type: ignore[assignment]

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    drive_folder_id: Mapped[str] = mapped_column(
        String(256), unique=True, nullable=False
    )
    users: Mapped[list["User"]] = relationship(back_populates="organisation")
