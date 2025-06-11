from app.extensions import db
from app.core.models.base import BaseModel

class User(BaseModel):
    __tablename__ = 'users'
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    google_id = db.Column(db.String, unique=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id'), nullable=False)
    organisation    = db.relationship('Organisation', backref='users')
