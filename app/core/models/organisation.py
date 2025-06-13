from app.extensions import db
from .base import BaseModel

class Organisation(BaseModel):
    __tablename__ = "organisations"

    name            = db.Column(db.String, unique=True, nullable=False)
    drive_folder_id = db.Column(db.String, nullable=False)