from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class FlaskBase(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=FlaskBase)

__all__ = ["db"]
