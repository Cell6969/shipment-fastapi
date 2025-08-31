from app.core.security import oauth2_scheme
from app.database.models import Seller
from app.database.redis import is_jti_blacklisted
from app.service.seller import SellerService
from app.service.shipment import ShipmentService
from app.database.session import get_session
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import decode_access_token
from uuid import UUID

SessionDepends = Annotated[AsyncSession, Depends(get_session)]


# shipment service
def get_shipment_service(session: SessionDepends):
    return ShipmentService(session=session)


# seller service
def get_seller_service(session: SessionDepends):
    return SellerService(session=session)


# access token dependency
async def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    data = decode_access_token(token)
    if data is None or await is_jti_blacklisted(data["jti"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    return data


# get current user
async def get_current_user(
    token_data: Annotated[dict, Depends(get_access_token)],
    session: SessionDepends,
) -> Seller:
    seller = await session.get(Seller, UUID(token_data["user"]["id"]))
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User"
        )
    return seller


SellerGuard = Annotated[Seller, Depends(get_current_user)]
ShipmentServiceDepends = Annotated[ShipmentService, Depends(get_shipment_service)]
SellerServiceDepends = Annotated[SellerService, Depends(get_seller_service)]
