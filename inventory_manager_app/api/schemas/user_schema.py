"""User schema."""

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    organisation_id: int
    allowed_channels: list[str]

    class Config:
        from_attributes = True
