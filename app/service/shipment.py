from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentUpdate,
    ShipmentUpdatePartial,
)
from app.database.models import DeliveryPartner, Seller, Shipment
from app.database.models import ShipmentStatus
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.database.redis import get_shipment_verification_code
from app.helper.datetimeconversion import to_naive_utc
from app.service.base import BaseService
from app.service.delivery_partner import DeliverPartnerService
from app.service.shipment_event import ShipmentEventService


class ShipmentService(BaseService[Shipment]):
    def __init__(
        self,
        session: AsyncSession,
        partner_service: DeliverPartnerService,
        event_service: ShipmentEventService,
    ):
        super().__init__(Shipment, session)
        self.partner_service = partner_service
        self.event_service = event_service

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
        # Assign delivery partner
        partner = await self.partner_service.assign_shipment(new_shipment)
        new_shipment.delivery_partner_id = partner.id

        # save shipment
        shipment = await self._add(new_shipment)

        # Add event service for shipment
        event = await self.event_service.add(
            shipment=shipment,
            location=seller.zip_code,
            status=ShipmentStatus.placed,
            description=f"assigned to a delivery partner {partner.name}",
        )
        shipment.timeline.append(event)

        return shipment

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
        self,
        id: UUID,
        shipment_update_partial: ShipmentUpdatePartial,
        partner: DeliveryPartner,
    ) -> Shipment:
        shipment = await self.get(id)

        if shipment.delivery_partner_id != partner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this shipment",
            )

        if shipment_update_partial.status == ShipmentStatus.delivered:
            code = await get_shipment_verification_code(shipment.id)
            if code != shipment_update_partial.verification_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="verification code is incorrect",
                )

        update = shipment_update_partial.model_dump(
            exclude_none=True,
            exclude={"verification_code"},
        )

        if not update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="no data provided"
            )

        if shipment_update_partial.estimated_delivery:
            update["estimated_delivery"] = shipment_update_partial.estimated_delivery

        shipment.sqlmodel_update(update)

        # add event
        if len(update) > 1 or not shipment_update_partial.estimated_delivery:
            await self.event_service.add(
                shipment=shipment,
                **update,
            )

        updated_shipment = await self._update(shipment)

        return updated_shipment

    async def delete(self, id: UUID) -> None:
        shipment = await self.get(id)
        await self._delete(shipment)

    async def cancel(self, id: UUID, seller: Seller) -> Shipment:
        # get shipment
        shipment = await self.get(id)

        # validate seller id
        if shipment.seller_id != seller.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not authorized to cancel this shipment",
            )

        event = await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
        )

        shipment.timeline.append(event)

        return shipment
