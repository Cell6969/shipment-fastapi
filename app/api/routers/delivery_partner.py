from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.delivery_partner import DeliveryPartnerUpdate
from app.api.dependencies import PartnerGuard, PartnerServiceDepends
from app.api.schemas.delivery_partner import DeliveryPartnerResponse
from app.helper.api import ApiResponse

router = APIRouter(prefix="/partner", tags=["partner"])


### login partner
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: PartnerServiceDepends,
) -> dict[str, str]:
    token = await service.token(request_form.username, request_form.password)
    return {"access_token": token, "type": "jwt"}


### update delivery partner
@router.post("/", response_model=ApiResponse[DeliveryPartnerResponse])
async def update_deliver_partner(
    partner: PartnerGuard,
    request: DeliveryPartnerUpdate,
    service: PartnerServiceDepends,
):
    return await service.update(partner.sqlmodel_update(request))
