from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
import jwt

from app.config import security_settings as settings
from app.api.schemas.seller import SellerCreate
from app.database.models import Seller
from app.utils import generate_access_token

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SellerService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, seller_create: SellerCreate) -> Seller:
        seller = Seller(
            **seller_create.model_dump(exclude={"password"}),
            # hash password
            password=hash_context.hash(seller_create.password)
        )
        self.session.add(seller)
        await self.session.commit()
        await self.session.refresh(seller)

        return seller

    async def token(self, email: str, password: str) -> str:
        result = await self.session.execute(
            select(Seller).where(Seller.email == email)   # type:ignore
        )
        seller = result.scalar()
        if seller is None or not hash_context.verify(password, seller.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid credentials",
            )
        token = generate_access_token(
            data={
                "user": {
                    "name": seller.name,
                    "id": seller.id,
                },
            }
        )

        return token
