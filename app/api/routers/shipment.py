from uuid import UUID
from fastapi import APIRouter

from app.api.dependencies import (
    PartnerServiceDepends,
    SellerGuard,
    ShipmentServiceDepends,
)
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentUpdate,
    ShipmentUpdatePartial,
)

router = APIRouter(prefix="/shipment", tags=["shipment"])


@router.get("/", response_model=list[ShipmentResponse])
async def get_shipment(seller_guard: SellerGuard, service: ShipmentServiceDepends):
    return await service.list()


@router.post("/", response_model=ShipmentResponse)
async def submit_shipment(
    body: ShipmentCreate, service: ShipmentServiceDepends, seller_guard: SellerGuard
):
    return await service.add(body, seller_guard)


@router.get("/{id}", response_model=ShipmentResponse)
async def get_shipment_by_id(id: str, service: ShipmentServiceDepends):
    return await service.get(UUID(id))


@router.put("/{id}", response_model=ShipmentResponse)
async def update_shipment(
    id: str, body: ShipmentUpdate, service: ShipmentServiceDepends
):
    return await service.update(UUID(id), body)


@router.patch("/{id}", response_model=ShipmentResponse)
async def patch_shipment(
    id: str,
    body: ShipmentUpdatePartial,
    service: ShipmentServiceDepends,
    partner: PartnerServiceDepends,
):
    return await service.update_partial(UUID(id), body)


@router.delete("/{id}")
async def delete_shipment(id: str, service: ShipmentServiceDepends) -> dict[str, str]:
    await service.delete(UUID(id))
    return {"message": f"shipment with id {id} deleted"}
