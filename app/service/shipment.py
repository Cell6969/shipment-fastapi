from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentUpdatePartial,
)
from app.database.models import Seller, Shipment
from app.database.models import ShipmentStatus
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.helper.datetimeconversion import to_naive_utc
from app.service.base import BaseService
from app.service.delivery_partner import DeliverPartnerService


class ShipmentService(BaseService[Shipment]):
    def __init__(self, session: AsyncSession, partner_service:DeliverPartnerService):
        super().__init__(Shipment, session)
        self.partner_service = partner_service

    async def list(self) -> Sequence[Shipment]:
        results = await self.session.execute(select(Shipment))
        return results.scalars().all()

    async def add(self, shipment_create: ShipmentCreate, seller: Seller) -> Shipment:
        new_shipment = Shipment(
            **shipment_create.model_dump(),
            status=ShipmentStatus.placed,
            estimated_delivery=datetime.now() + timedelta(days=3),
            seller_id=seller.id,
        )
        partner = await self.partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner_id = partner.id
        return await self._add(new_shipment)

    async def get(self, id: UUID) -> Shipment:
        shipment = await self._get(id)
        if shipment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="shipment is not found"
            )
        return shipment

    async def update(self, id: UUID, shipment_update: ShipmentUpdate) -> Shipment:
        shipment = await self.get(id)
        data = shipment_update.model_dump()
        if "estimated_delivery" in data:
            data["estimated_delivery"] = to_naive_utc(data["estimated_delivery"])
        shipment.sqlmodel_update(data)
        
        updated_shipment = await self._update(shipment)

        return updated_shipment

    async def update_partial(
        self, id: UUID, shipment_update_partial: ShipmentUpdatePartial
    ) -> Shipment:
        shipment = await self.get(id)
        update = shipment_update_partial.model_dump(exclude_none=True)

        if "estimated_delivery" in update:
            update["estimated_delivery"] = to_naive_utc(update["estimated_delivery"])
        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="no data provided"
            )
        shipment.sqlmodel_update(update)
        updated_shipment = await self._update(shipment)

        return updated_shipment

    async def delete(self, id: UUID) -> None:
        shipment = await self.get(id)
        await self._delete(shipment)
