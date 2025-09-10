from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.api.dependencies import (
    SellerServiceDepends,
    SessionDepends,
    get_seller_access_token,
)
from app.api.schemas.seller import SellerCreate, SellerResponse
from app.config import app_settings
from app.database.models import Seller
from app.database.redis import add_jti_to_blacklist
from app.helper.api import ApiResponse
from app.core.security import oauth2_scheme_seller
from app.utils import TEMPLATE_DIR, decode_access_token


router = APIRouter(prefix="/seller", tags=["seller"])


# register
@router.post("/signup", response_model=ApiResponse[SellerResponse])
async def register_seller(
    body: SellerCreate,
    service: SellerServiceDepends,
):
    seller = await service.create(body)
    return ApiResponse.success("seller created successfully", seller)


# login
@router.post("/token")
async def login_seller(
    request_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: SellerServiceDepends,
) -> dict[str, str]:
    token = await service.token(request_form.username, request_form.password)
    return {"access_token": token, "type": "jwt"}


# verify
@router.get("/verify")
async def verify_seller_email(
    token: str,
    service: SellerServiceDepends,
) -> dict[str, str]:
    await service.verify_email(token)
    return {"detail": "email verified successfully"}


# verify
@router.get("/forgot-password")
async def forgot_seller_password(
    email: EmailStr,
    service: SellerServiceDepends,
) -> dict[str, str]:
    await service.send_password_link(email, "seller")
    return {"detail": "password reset link sent successfully"}


# form-reset
@router.get("/reset-password")
async def form_reset_seller_password(
    request: Request,
    token: str,
    service: SellerServiceDepends,
):
    templates = Jinja2Templates(directory=TEMPLATE_DIR / "password")
    return templates.TemplateResponse(
        request=request,
        name="reset.html",
        context={
            "reset_url": f"{app_settings.APP_DOMAIN}{router.prefix}/reset-password?token={token}",
        },
    )


# reset
@router.post("/reset-password")
async def submit_reset_seller_password(
    request: Request,
    token: str,
    password: Annotated[str, Form()],
    service: SellerServiceDepends,
):
    res = await service.reset_password(token, password)

    templates = Jinja2Templates(directory=TEMPLATE_DIR / "password")
    return templates.TemplateResponse(
        request=request,
        name="reset_success.html" if res else "reset_failed.html",
    )


# dashboard
@router.get("/dashboard")
async def get_dashboard(
    token: Annotated[str, Depends(oauth2_scheme_seller)], session: SessionDepends
):
    data = decode_access_token(token)
    if data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
        )

    seller = await session.get(Seller, data["user"]["id"])

    return ApiResponse.success("dashboard", seller)


# logout user
@router.get("/logout")
async def logout_seller(token_data: Annotated[dict, Depends(get_seller_access_token)]):
    await add_jti_to_blacklist(token_data["jti"])
    return {"detail": "logout successfully"}
