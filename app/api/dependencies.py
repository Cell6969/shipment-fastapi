from app.service.shipment import ShipmentService
from app.database.session import get_session
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


SessionDepends = Annotated[AsyncSession, Depends(get_session)]

def get_shipment_service(session:SessionDepends):
    return ShipmentService(session=session)

ServiceDepends = Annotated[ShipmentService, Depends(get_shipment_service)]