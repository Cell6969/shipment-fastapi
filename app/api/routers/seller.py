from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SellerServiceDepends, SessionDepends
from app.api.schemas.seller import SellerCreate, SellerResponse
from app.database.models import Seller
from app.helper.api import ApiResponse
from app.core.security import oauth2_scheme
from app.utils import decode_access_token


router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("/signup", response_model=ApiResponse[SellerResponse])
async def register_seller(
    body: SellerCreate,
    service: SellerServiceDepends,
):
    seller = await service.create(body)
    return ApiResponse.success("seller created successfully", seller)


@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDepends,
) -> dict[str, str]:
    token = await service.token(request_form.username, request_form.password)
    return {"access_token": token, "type": "jwt"}


@router.get("/dashboard")
async def get_dashboard(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDepends
):
    data = decode_access_token(token)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )

    seller = await session.get(Seller, data["user"]["id"])

    return ApiResponse.success("dashboard", seller)
