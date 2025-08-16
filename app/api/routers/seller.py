from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SellerServiceDepends
from app.api.schemas.seller import SellerCreate, SellerResponse


router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("/signup", response_model=SellerResponse)
async def register_seller(
    body: SellerCreate,
    service: SellerServiceDepends,
):
    return await service.create(body)


@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDepends,
) -> dict[str, str]:
    token = await service.token(request_form.username, request_form.password)
    return {
        "access_token": token,
        "type": "JWT"
    }
