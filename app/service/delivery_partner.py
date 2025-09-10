from typing import Sequence

from fastapi import HTTPException, status
from sqlmodel import select, any_
from app.service.user import UserService
from app.database.models import DeliveryPartner, Shipment
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.delivery_partner import DeliveryPartnerCreate
from fastapi import BackgroundTasks


class DeliverPartnerService(UserService[DeliveryPartner]):
    def __init__(self, session: AsyncSession, tasks: BackgroundTasks):
        super().__init__(DeliveryPartner, session, tasks)

    async def create(
        self, delivery_partner_create: DeliveryPartnerCreate
    ) -> DeliveryPartner:
        return await self._add_user(
            delivery_partner_create.model_dump(),
            "partner"
        )

    async def token(self, email: str, password: str) -> str:
        return await self._generate_token(email, password)

    async def update(self, partner: DeliveryPartner) -> DeliveryPartner:
        return await self._update(partner)

    async def get_partner_by_zipcode(self, zipcode: int) -> Sequence[DeliveryPartner]:
        return (
            await self.session.scalars(
                select(DeliveryPartner).where(
                    zipcode == any_(DeliveryPartner.serviceable_zip_codes)
                )
            )
        ).all()

    async def assign_shipment(self, shipment: Shipment) -> DeliveryPartner:
        eligible_partners = await self.get_partner_by_zipcode(shipment.destination)
        for partner in eligible_partners:
            if partner.current_handling_capacity > 0:
                partner.shipments.append(shipment)
                return partner

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="No available partner found",
        )
