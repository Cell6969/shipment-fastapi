from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from app.api.schemas.seller import SellerResponse
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
    id:UUID
    status: ShipmentStatus
    estimated_delivery: datetime
    seller: SellerResponse
