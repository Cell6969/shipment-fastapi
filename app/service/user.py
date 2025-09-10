from typing import Generic, TypeVar
from fastapi import BackgroundTasks, HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from app.config import app_settings
from app.service.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from passlib.context import CryptContext

from app.service.notification import NotificationService
from app.utils import generate_access_token, generate_url_safe_token


U = TypeVar("U", bound=User)
hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(Generic[U],BaseService[U]):
    def __init__(self, model: type[U], session: AsyncSession, tasks: BackgroundTasks):
        self.model = model
        self.session = session
        self.notification_service = NotificationService(tasks=tasks)

    async def _add_user(self, data: dict, router_prefix:str) -> U:
        data["password"] = hash_context.hash(data["password"])
        user = self.model(**data)

        user = await self._add(user)

        # generate url safe token
        token = generate_url_safe_token({
            "email": user.email,
            "id": user.id #type:ignore
        })

        await self.notification_service.send_email_with_template(
            recipients=[user.email],
            subject="verify your account with fastship",
            context={
                "username": user.name,
                "verification_url": f"{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}"
            },
            template="mail_verified_email.html"
        )

        return user 

    async def _get_by_email(self, email: str) -> U | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email) #type:ignore
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

        if not user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="email not verified",
            )
        
        return generate_access_token(
            data= {
                "user": {
                    "name": user.name,
                    "id": str(user.id) #type:ignore
                }
            }
        )
