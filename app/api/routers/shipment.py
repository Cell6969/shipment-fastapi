from uuid import UUID
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.dependencies import (
    PartnerGuard,
    SellerGuard,
    ShipmentServiceDepends,
)
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentUpdatePartial,
)
from app.utils import TEMPLATE_DIR

router = APIRouter(prefix="/shipment", tags=["shipment"])

templates = Jinja2Templates(directory=TEMPLATE_DIR)


@router.get("/", response_model=list[ShipmentResponse])
async def get_shipment(_: SellerGuard, service: ShipmentServiceDepends):
    return await service.list()


@router.get("/tracking")
async def get_shipment_tracking(
    request: Request, id: str, service: ShipmentServiceDepends
):
    shipment = await service.get(UUID(id))

    context = shipment.model_dump()
    context["partner"] = shipment.delivery_partner.name
    context["status"] = shipment.status
    context["timeline"] = shipment.timeline
    context["timeline"].reverse()

    return templates.TemplateResponse(
        request=request,
        name="track.html",
        context=context,
    )


@router.post("/", response_model=ShipmentResponse)
async def submit_shipment(
    body: ShipmentCreate, service: ShipmentServiceDepends, seller_guard: SellerGuard
):
    return await service.add(body, seller_guard)


# cancel
@router.get("/cancel", response_model=ShipmentResponse)
async def cancel_shipment(
    id: str,
    service: ShipmentServiceDepends,
    seller: SellerGuard,
):
    return await service.cancel(UUID(id), seller)


@router.get("/{id}", response_model=ShipmentResponse)
async def get_shipment_by_id(id: str, service: ShipmentServiceDepends):
    return await service.get(UUID(id))


# @router.put("/{id}", response_model=ShipmentResponse)
# async def update_shipment(
#     id: str, body: ShipmentUpdate, service: ShipmentServiceDepends
# ):
#     return await service.update(UUID(id), body)


@router.patch("/{id}", response_model=ShipmentResponse)
async def patch_shipment(
    id: str,
    body: ShipmentUpdatePartial,
    service: ShipmentServiceDepends,
    partner: PartnerGuard,
):
    return await service.update_partial(UUID(id), body, partner)


@router.delete("/{id}")
async def delete_shipment(
    id: str,
    service: ShipmentServiceDepends,
    seller: SellerGuard,
) -> dict[str, str]:
    await service.delete(UUID(id))
    return {"message": f"shipment with id {id} deleted"}
