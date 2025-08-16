from datetime import datetime
from pydantic import BaseModel, Field

from app.database.models import ShipmentStatus

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
    status: ShipmentStatus | None = None
    estimated_delivery: datetime | None = None

class ShipmentResponse(BaseShipment):
    id:int
    status: ShipmentStatus
    estimated_delivery: datetime
