from app.service.user import UserService
from app.database.models import DeliveryPartner
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.delivery_partner import DeliveryPartnerCreate


class DeliverPartnerService(UserService[DeliveryPartner]):
    def __init__(self, session: AsyncSession):
        super().__init__(DeliveryPartner, session)

    async def create(
        self, delivery_partner_create: DeliveryPartnerCreate
    ) -> DeliveryPartner:
        return await self._add_user(
            **delivery_partner_create.model_dump(),
        )

    async def token(self, email:str, password:str) -> str:
        return await self._generate_token(email, password)

    async def update(self, partner:DeliveryPartner) -> DeliveryPartner:
        return await self._update(partner)