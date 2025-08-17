from fastapi import APIRouter

from app.api.dependencies import SellerGuard, ShipmentServiceDepends
from app.api.schemas.schemas import ShipmentCreate, ShipmentResponse, ShipmentUpdate, ShipmentUpdatePartial

router = APIRouter(prefix="/shipment", tags=["shipment"])

@router.get("/", response_model=list[ShipmentResponse])
async def get_shipment(service:ShipmentServiceDepends):
    return await service.list()

@router.post("/", response_model=ShipmentResponse)
async def submit_shipment(body:ShipmentCreate, service:ShipmentServiceDepends, seller_guard: SellerGuard):
    return await service.add(body)

@router.get("/{id}", response_model=ShipmentResponse)
async def get_shipment_by_id(id:int, service:ShipmentServiceDepends):
    return await service.get(id)

@router.put("/{id}", response_model=ShipmentResponse)
async def update_shipment(id:int, body:ShipmentUpdate, service:ShipmentServiceDepends):
    return await service.update(id, body)

@router.patch("/{id}", response_model=ShipmentResponse)
async def patch_shipment(id:int, body:ShipmentUpdatePartial, service:ShipmentServiceDepends):
    return await service.update_partial(id, body)

@router.delete("/{id}")
async def delete_shipment(id:int, service:ShipmentServiceDepends) -> dict[str, str]:
    await service.delete(id)
    return {"message": f"shipment with id {id} deleted"}