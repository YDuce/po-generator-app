from __future__ import annotations

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = 'user'
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    organisation_id: Mapped[int] = mapped_column(ForeignKey('organisation.id'), nullable=False)
    organisation: Mapped['Organisation'] = relationship(back_populates='users')
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    allowed_channels: Mapped[list[str]] = mapped_column(JSON, default=list)
