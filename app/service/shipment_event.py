from app.service.base import BaseService
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession


class ShipmentEventService(BaseService[ShipmentEvent]):
    def __init__(self, session: AsyncSession):
        super().__init__(ShipmentEvent, session)

    async def add(
        self,
        shipment: Shipment,
        location: int | None = None,
        status: ShipmentStatus | None = None,
        description: str | None = None,
    ) -> ShipmentEvent:
        if not location or not status:
            last_event = await self.get_latest_event(shipment=shipment)
            location = location if location else last_event.location
            status = status if status else last_event.status

        new_event = ShipmentEvent(
            location=location,
            status=status,
            description=(
                description
                if description
                else self._generate_description(status, location)
            ),
            shipment_id=shipment.id,
        )

        return await self._add(new_event)

    async def get_latest_event(self, shipment: Shipment) -> ShipmentEvent:
        timeline = shipment.timeline
        timeline.sort(key=lambda item: item.created_at)
        return timeline[-1]

    def _generate_description(self, status: ShipmentStatus, location: int):
        match status:
            case ShipmentStatus.placed:
                return "assigned delivery partner"
            case ShipmentStatus.out_for_delivery:
                return "shipment out for delivery"
            case ShipmentStatus.delivered:
                return "successfully delivered"
            case _:  # shipment in transit
                return f"scanned at location {location}"
