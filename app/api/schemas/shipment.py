from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.api.schemas.seller import SellerResponse
from app.database.models import ShipmentEvent, ShipmentStatus

class BaseShipment(BaseModel):
    content: str = Field(max_length=100)
    weight: float = Field(lt=25, ge=0, description="weight of content")
    destination:int

class ShipmentCreate(BaseShipment):
    pass
    
class ShipmentUpdate(BaseModel):
    status: ShipmentStatus
    estimated_delivery: datetime

class ShipmentUpdatePartial(BaseModel):
    location: int | None = Field(default=None)
    description: str | None = Field(default=None)
    status: ShipmentStatus | None = Field(default=None)
    estimated_delivery: datetime | None = Field(default=None)

class ShipmentResponse(BaseShipment):
    id:UUID
    timeline: list[ShipmentEvent]
    estimated_delivery: datetime
