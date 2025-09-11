from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from app.api.schemas.seller import SellerResponse
from app.database.models import ShipmentEvent, ShipmentStatus


class BaseShipment(BaseModel):
    content: str = Field(max_length=100)
    weight: float = Field(lt=25, ge=0, description="weight of content")
    destination: int


class ShipmentCreate(BaseShipment):
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)


class ShipmentUpdate(BaseModel):
    status: ShipmentStatus
    estimated_delivery: datetime


class ShipmentUpdatePartial(BaseModel):
    location: int | None = Field(default=None)
    description: str | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    verification_code: str | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)


class ShipmentResponse(BaseShipment):
    id: UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
    client_contact_email: EmailStr
    client_contact_phone: str | None = Field(default=None)


class ShipmentReview(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: str | None = Field(default=None)
