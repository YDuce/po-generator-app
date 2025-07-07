from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from inventory_manager_app.extensions import db


class Base(db.Model):
    """Base model with automatic table name and integer primary key."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
