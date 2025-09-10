from random import randint
from fastapi import BackgroundTasks
from app.database.redis import add_shipment_verification_code
from app.service.base import BaseService
from app.database.models import Shipment, ShipmentEvent, ShipmentStatus
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.notification import NotificationService
from app.utils import generate_verification_code


class ShipmentEventService(BaseService[ShipmentEvent]):
    def __init__(self, session: AsyncSession, tasks: BackgroundTasks):
        super().__init__(ShipmentEvent, session)
        self.notification_service = NotificationService(tasks)

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

        # send notification
        await self._notify(shipment=shipment, status=status)

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
            case ShipmentStatus.cancelled:
                return "cancelled by seller"
            case _:  # shipment in transit
                return f"scanned at location {location}"

    async def _notify(self, shipment: Shipment, status: ShipmentStatus):
        if status == ShipmentStatus.in_transit :
            return

        subject: str
        context = {}
        template_name:str

        match (status):
            case ShipmentStatus.placed:
                subject="Your Order is Shipped 🚛"
                context["seller"] = shipment.seller.name
                context["partner"] = shipment.delivery_partner.name
                context["id"] = shipment.id
                template_name="mail_placed.html"

            case ShipmentStatus.out_for_delivery:
                subject="Your Order is Arriving Soon 🛵"
                template_name = "mail_out_for_delivery.html"

                code = generate_verification_code()
                await add_shipment_verification_code(shipment.id, code)

                ### TEMPORARY NOT USE SMS
                # if shipment.client_contact_phone:
                #     await self.notification_service.send_sms(
                #         to=str(shipment.client_contact_phone),
                #         body=f"Your order is arriving soon! Share the code {code} "
                #         "with your delivery to verify your order.",
                #     )
                # else:
                #     context["verification_code"] = code

                context["verification_code"] = code
                
            case ShipmentStatus.delivered:
                subject = "Your Order is Delivered ✅"
                context["seller"] = shipment.seller.name
                template_name = "mail_delivered.html"

            case ShipmentStatus.cancelled:
                subject = "Your Order is Cancelled ❌"
                template_name = "mail_cancelled.html"
        
        await self.notification_service.send_email_with_template(
            recipients=[shipment.client_contact_email],
            subject=subject,
            context=context,
            template_name=template_name,
        )
