from app.core.security import oauth2_scheme_seller, oauth2_scheme_partner
from app.database.models import DeliveryPartner, Seller
from app.database.redis import is_jti_blacklisted
from app.service.seller import SellerService
from app.service.shipment import ShipmentService
from app.database.session import get_session
from typing import Annotated
from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.service.shipment_event import ShipmentEventService
from app.utils import decode_access_token
from uuid import UUID
from app.service.delivery_partner import DeliverPartnerService

SessionDepends = Annotated[AsyncSession, Depends(get_session)]


# shipment service
def get_shipment_service(session: SessionDepends, tasks: BackgroundTasks):
    return ShipmentService(
        session=session,
        partner_service=DeliverPartnerService(session=session),
        event_service=ShipmentEventService(session=session, tasks=tasks),
    )


# seller service
def get_seller_service(session: SessionDepends):
    return SellerService(session=session)


# delivery partner service
def get_delivery_partner_service(session: SessionDepends):
    return DeliverPartnerService(session=session)


# access token dependency
async def _get_access_token(token: str):
    data = decode_access_token(token)
    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    return data


# get access token seller
async def get_seller_access_token(token: Annotated[str, Depends(oauth2_scheme_seller)]):
    return await _get_access_token(token)


# get access token partner
async def get_partner_access_token(
    token: Annotated[str, Depends(oauth2_scheme_partner)],
):
    return await _get_access_token(token)


# get current seller
async def get_current_seller(
    token_data: Annotated[dict, Depends(get_seller_access_token)],
    session: SessionDepends,
) -> Seller:
    seller = await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User"
        )
    return seller


async def get_current_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
    session: SessionDepends,
) -> DeliveryPartner:
    partner = await session.get(DeliveryPartner, UUID(token_data["user"]["id"]))
    if partner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User"
        )
    return partner


# Guard
SellerGuard = Annotated[Seller, Depends(get_current_seller)]
PartnerGuard = Annotated[DeliveryPartner, Depends(get_current_partner)]

# Service
ShipmentServiceDepends = Annotated[ShipmentService, Depends(get_shipment_service)]
SellerServiceDepends = Annotated[SellerService, Depends(get_seller_service)]
PartnerServiceDepends = Annotated[
    DeliverPartnerService, Depends(get_delivery_partner_service)
]
