from app.service.seller import SellerService
from app.service.shipment import ShipmentService
from app.database.session import get_session
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


SessionDepends = Annotated[AsyncSession, Depends(get_session)]

# shipment service
def get_shipment_service(session:SessionDepends):
    return ShipmentService(session=session)

def get_seller_service(session:SessionDepends):
    return SellerService(session=session)

ShipmentServiceDepends = Annotated[ShipmentService, Depends(get_shipment_service)]
SellerServiceDepends = Annotated[SellerService, Depends(get_seller_service)]