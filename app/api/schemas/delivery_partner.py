from typing import Sequence
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class BaseDeliveryPartner(BaseModel):
    name: str
    email: EmailStr
    serviceable_zip_codes: Sequence[int]
    max_handling_capacity: int


class DeliveryPartnerCreate(BaseDeliveryPartner):
    password: str


class DeliveryPartnerUpdate(BaseModel):
    serviceable_zip_codes: Sequence[int] | None = Field(default=None)
    max_handling_capacity: int | None = Field(default=None)


class DeliveryPartnerResponse(BaseDeliveryPartner):
    id: UUID
