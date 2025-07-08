from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from typing import TYPE_CHECKING
from inventory_manager_app.extensions import db, FlaskBase

if TYPE_CHECKING:
    class Base(FlaskBase):
        ...
else:
    class Base(db.Model):
        __abstract__ = True
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
