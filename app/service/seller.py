from datetime import datetime, timedelta
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
import jwt

from app.config import security_settings as settings
from app.api.schemas.seller import SellerCreate
from app.database.models import Seller
from app.service.user import UserService
from app.utils import generate_access_token
from fastapi import BackgroundTasks

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SellerService(UserService[Seller]):
    def __init__(self, session: AsyncSession, tasks: BackgroundTasks):
        super().__init__(Seller, session, tasks)

    async def create(self, seller_create: SellerCreate) -> Seller:
        return await self._add_user(seller_create.model_dump(), "seller")

    async def token(self, email: EmailStr, password: str) -> str:
        return await self._generate_token(email, password)
