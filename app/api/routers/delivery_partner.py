from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.schemas.delivery_partner import (
    DeliveryPartnerCreate,
    DeliveryPartnerUpdate,
)
from app.api.dependencies import (
    PartnerGuard,
    PartnerServiceDepends,
    get_partner_access_token,
)
from app.api.schemas.delivery_partner import DeliveryPartnerResponse
from app.database.redis import add_jti_to_blacklist
from app.helper.api import ApiResponse

router = APIRouter(prefix="/partner", tags=["partner"])


### signup partner
@router.post("/signup", response_model=ApiResponse[DeliveryPartnerResponse])
async def register_delivery_partner(
    body: DeliveryPartnerCreate, service: PartnerServiceDepends
):
    partner = await service.create(body)
    return ApiResponse.success("partner created successfully", partner)


### login partner
@router.post("/token")
async def login_delivery_partner(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: PartnerServiceDepends,
) -> dict[str, str]:
    token = await service.token(request_form.username, request_form.password)
    return {"access_token": token, "type": "jwt"}


### verify partner
@router.get("/verify")
async def verify_partner(
    token: str,
    service: PartnerServiceDepends,
) -> dict[str, str]:
    await service.verify_email(token)
    return {"detail": "email verified successfully"}


### update delivery partner
@router.post("/", response_model=ApiResponse[DeliveryPartnerResponse])
async def update_deliver_partner(
    partner: PartnerGuard,
    request: DeliveryPartnerUpdate,
    service: PartnerServiceDepends,
):
    # update data with given fields
    update = request.model_dump(exclude_none=True)

    if not update:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="no data provided"
        )

    result = await service.update(partner.sqlmodel_update(update))

    return ApiResponse.success("partner updated successfully", result)


### logout
@router.get("/logout")
async def logout_partner(
    token_data: Annotated[dict, Depends(get_partner_access_token)],
) -> dict[str, str]:
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "logout successfully"}
