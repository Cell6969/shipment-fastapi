from typing import Generic, TypeVar
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from app.service.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from passlib.context import CryptContext

from app.utils import generate_access_token


U = TypeVar("U", bound=User)
hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(Generic[U],BaseService[U]):
    def __init__(self, model: type[U], session: AsyncSession):
        self.model = model
        self.session = session

    async def _add_user(self, data: dict) -> U:
        user = self.model(
            **data,
            password=hash_context.hash(data["password"]),
        )
        return await self._add(user)

    async def _get_by_email(self, email: str) -> U | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == EmailStr(email))
        )

    async def _generate_token(self, email: str, password: str) -> str:
        # get user by email
        user = await self._get_by_email(email)

        if user is None or not hash_context.verify(
            password,
            user.password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid credentials",
            )
        
        return generate_access_token(
            data= {
                "user": {
                    "name": user.name,
                    "id": str(user.id) #type:ignore
                }
            }
        )
