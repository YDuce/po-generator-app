from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, model_validator


class OrderPayload(BaseModel):
    order_id: str
    channel: str
    product_sku: str
    quantity: int
    ordered_date: datetime | None = None


class UserSchema(BaseModel):
    id: int
    email: EmailStr
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


class NewReallocationPayload(BaseModel):
    sku: str
    channel_origin: str
    reason: str

    @model_validator(mode="after")
    def check_reason(self) -> "NewReallocationPayload":
        if self.reason not in {"slow-mover", "out-of-stock"}:
            raise ValueError("Invalid reason")
        return self


class BatchReallocationPayload(BaseModel):
    items: list[NewReallocationPayload]

    @model_validator(mode="after")
    def check_duplicates(self) -> "BatchReallocationPayload":
        seen = set()
        for idx, item in enumerate(self.items):
            key = (item.sku, item.channel_origin, item.reason)
            if key in seen:
                raise ValueError(f"Duplicate reallocation at index {idx}: {key}")
            seen.add(key)
        return self
