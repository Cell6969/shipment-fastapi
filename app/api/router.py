from fastapi import APIRouter

from app.api.dependencies import ServiceDepends
from app.api.schemas.schemas import ShipmentCreate, ShipmentResponse, ShipmentUpdate, ShipmentUpdatePartial

router = APIRouter()

@router.get("/shipment", response_model=list[ShipmentResponse])
async def get_shipment(service:ServiceDepends):
    return await service.list()

@router.post("/shipment", response_model=ShipmentResponse)
async def submit_shipment(body:ShipmentCreate, service:ServiceDepends):
    return await service.add(body)

@router.get("/shipment/{id}", response_model=ShipmentResponse)
async def get_shipment_by_id(id:int, service:ServiceDepends):
    return await service.get(id)

@router.put("/shipment/{id}", response_model=ShipmentResponse)
async def update_shipment(id:int, body:ShipmentUpdate, service:ServiceDepends):
    return await service.update(id, body)

@router.patch("/shipment/{id}", response_model=ShipmentResponse)
async def patch_shipment(id:int, body:ShipmentUpdatePartial, service:ServiceDepends):
    return await service.update_partial(id, body)

@router.delete("/shipment/{id}")
async def delete_shipment(id:int, service:ServiceDepends) -> dict[str, str]:
    await service.delete(id)
    return {"message": f"shipment with id {id} deleted"}