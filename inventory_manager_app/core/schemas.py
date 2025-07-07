from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, model_validator


class OrderPayload(BaseModel):
    order_id: str
    channel: str
    product_sku: str
    quantity: int
    ordered_date: datetime | None = None


class UserSchema(BaseModel):
    id: int
    email: str
    organisation_id: int
    roles: list[str]


class OrganisationSchema(BaseModel):
    id: int
    name: str
    drive_folder_id: str


class ReallocationSchema(BaseModel):
    id: int
    sku: str
    channel_origin: str
    reason: str
    added_date: datetime


class ReallocationCreatePayload(BaseModel):
    sku: str
    channel_origin: str
    reason: str

    @model_validator(mode="after")
    def check_reason(self) -> "ReallocationCreatePayload":
        if self.reason not in {"slow-mover", "out-of-stock"}:
            raise ValueError("Invalid reason")
        return self
