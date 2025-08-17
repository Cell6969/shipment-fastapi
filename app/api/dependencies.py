from app.core.security import oauth2_scheme
from app.database.models import Seller
from app.service.seller import SellerService
from app.service.shipment import ShipmentService
from app.database.session import get_session
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import decode_access_token


SessionDepends = Annotated[AsyncSession, Depends(get_session)]


# shipment service
def get_shipment_service(session: SessionDepends):
    return ShipmentService(session=session)


# seller service
def get_seller_service(session: SessionDepends):
    return SellerService(session=session)


# access token dependency
def get_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    data = decode_access_token(token)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )
    return data


# get current user
async def get_current_user(
    token_data: Annotated[dict, Depends(get_access_token)],
    session: SessionDepends,
) -> Seller:
    seller = await session.get(Seller, token_data["user"]["id"])
    if seller is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )
    return seller


SellerGuard = Annotated[Seller, Depends(get_current_user)]
ShipmentServiceDepends = Annotated[ShipmentService, Depends(get_shipment_service)]
SellerServiceDepends = Annotated[SellerService, Depends(get_seller_service)]
