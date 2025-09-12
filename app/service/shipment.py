from typing import Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.api.schemas.shipment import (
    ShipmentCreate,
    ShipmentReview,
    ShipmentUpdate,
    ShipmentUpdatePartial,
)
from app.core.exception import BadRequest, ClientNotAuthorized, EntityNotFound, InvalidToken
from app.database.models import DeliveryPartner, Review, Seller, Shipment, TagName
from app.database.models import ShipmentStatus
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.database.redis import get_shipment_verification_code
from app.helper.datetimeconversion import to_naive_utc
from app.service.base import BaseService
from app.service.delivery_partner import DeliverPartnerService
from app.service.shipment_event import ShipmentEventService
from app.utils import decode_url_safe_token


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
            raise EntityNotFound()
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
            raise ClientNotAuthorized()

        if shipment_update_partial.status == ShipmentStatus.delivered:
            code = await get_shipment_verification_code(shipment.id)
            if code != shipment_update_partial.verification_code:
                raise ClientNotAuthorized()

        update = shipment_update_partial.model_dump(
            exclude_none=True,
            exclude={"verification_code"},
        )

        if not update:
            raise BadRequest()

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
            raise ClientNotAuthorized()

        event = await self.event_service.add(
            shipment=shipment,
            status=ShipmentStatus.cancelled,
        )

        shipment.timeline.append(event)

        return shipment

    async def rate(self, token: str, rating: int, comment: str | None = None):
        token_data = decode_url_safe_token(
            token=token, expiry=timedelta(days=1), salt="shipment-review"
        )
        if not token_data:
            raise InvalidToken()

        shipment = await self.get(UUID(token_data["id"]))

        review_model = Review(
            rating=rating,
            comment=comment if comment else None,
            shipment_id=shipment.id,
        )

        self.session.add(review_model)
        await self.session.commit()

        return review_model

    async def add_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)
        tag = await tag_name.tag(self.session)
        if tag is None:
            raise EntityNotFound()

        shipment.tags.append(tag)
        return await self._update(shipment)

    async def remove_tag(self, id: UUID, tag_name: TagName):
        shipment = await self.get(id)

        try:
            tag = await tag_name.tag(self.session)
            if tag is None:
                raise EntityNotFound()
            shipment.tags.remove(tag)
            return await self._update(shipment)

        except Exception:
            raise EntityNotFound()
