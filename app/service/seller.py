from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.api.schemas.seller import SellerCreate
from app.database.models import Seller

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, seller_create: SellerCreate) -> Seller:
        seller = Seller(
            **seller_create.model_dump(exclude=["password"]),
            # hash password
            password=hash_context.hash(seller_create.password)
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller