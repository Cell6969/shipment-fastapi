from fastapi import APIRouter

from app.api.routers import delivery_partner
from .routers import shipment, seller

master_router = APIRouter()

# register all routes
master_router.include_router(shipment.router)
master_router.include_router(seller.router)
master_router.include_router(delivery_partner.router)