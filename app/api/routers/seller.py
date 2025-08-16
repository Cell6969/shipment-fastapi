from fastapi import APIRouter

from app.api.dependencies import SellerServiceDepends
from app.api.schemas.seller import SellerCreate, SellerResponse


router = APIRouter(prefix="/seller", tags=["seller"])


@router.post("/signup", response_model=SellerResponse)
async def register_seller(
    body: SellerCreate,
    service: SellerServiceDepends,
):
    return await service.create(body)
