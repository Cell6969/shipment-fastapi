from datetime import timedelta
from typing import Generic, TypeVar
from uuid import UUID
from fastapi import BackgroundTasks, HTTPException, status
from pydantic import EmailStr
from sqlalchemy import select
from app.config import app_settings
from app.core.exception import BadCredentials, EntityNotFound, InvalidToken
from app.service.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from passlib.context import CryptContext

from app.service.notification import NotificationService
from app.utils import (
    decode_url_safe_token,
    generate_access_token,
    generate_url_safe_token,
)
from app.worker.tasks import send_email_with_template


U = TypeVar("U", bound=User)
hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(Generic[U], BaseService[U]):
    def __init__(self, model: type[U], session: AsyncSession, tasks: BackgroundTasks):
        self.model = model
        self.session = session
        self.notification_service = NotificationService(tasks=tasks)

    async def _add_user(self, data: dict, router_prefix: str) -> U:
        data["password"] = hash_context.hash(data["password"])
        user = self.model(**data)

        user = await self._add(user)

        # generate url safe token
        token = generate_url_safe_token({"id": str(user.id)})  # type:ignore

        ### Use from background task
        # await self.notification_service.send_email_with_template(
        #     recipients=[user.email],
        #     subject="verify your account with fastship",
        #     context={
        #         "username": user.name,
        #         "verification_url": f"{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}",
        #     },
        #     template_name="mail_verified_email.html",
        # )

        ### Use Celery
        send_email_with_template.delay(
            recipients=[user.email],
            subject="verify your account with fastship",
            context={
                "username": user.name,
                "verification_url": f"{app_settings.APP_DOMAIN}/{router_prefix}/verify?token={token}",
            },
            template_name="mail_verified_email.html",
        )

        return user

    async def verify_email(self, token: str):
        token_data = decode_url_safe_token(token)
        if not token_data:
            raise InvalidToken()

        user = await self._get(UUID(token_data["id"]))
        if user is None:
            raise EntityNotFound()

        user.email_verified = True
        await self._update(user)

    async def _get_by_email(self, email: str) -> U | None:
        return await self.session.scalar(
            select(self.model).where(self.model.email == email)  # type:ignore
        )

    async def _generate_token(self, email: str, password: str) -> str:
        # get user by email
        user = await self._get_by_email(email)

        if user is None or not hash_context.verify(
            password,
            user.password,
        ):
            raise BadCredentials()

        if not user.email_verified:
            raise BadCredentials()

        return generate_access_token(
            data={
                "user": {
                    "name": user.name,
                    "id": str(user.id),  # type:ignore
                }
            }
        )

    async def send_password_link(self, email: EmailStr, router_prefix: str):
        user = await self._get_by_email(email=email)
        if user is None:
            raise EntityNotFound()

        token = generate_url_safe_token(
            {"id": str(user.id)}, salt="password-reset" # type:ignore
        )  

        ### Use from background task
        # await self.notification_service.send_email_with_template(
        #     recipients=[user.email],
        #     subject="reset your password from fastship",
        #     context={
        #         "username": user.name,
        #         "reset_password_url": f"{app_settings.APP_DOMAIN}/{router_prefix}/reset-password?token={token}",
        #     },
        #     template_name="mail_reset_password.html",
        # )

        ### Use Celery
        send_email_with_template.delay(
            recipients=[user.email],
            subject="reset your password from fastship",
            context={
                "username": user.name,
                "reset_password_url": f"{app_settings.APP_DOMAIN}/{router_prefix}/reset-password?token={token}",
            },
            template_name="mail_reset_password.html",
        )

    async def reset_password(self, token: str, password: str) -> bool:
        token_data = decode_url_safe_token(
            token,
            salt="password-reset",
            expiry=timedelta(days=1),
        )

        if not token_data:
            return False

        user = await self._get(UUID(token_data["id"]))
        if user is None:
            return False

        user.password = hash_context.hash(password)
        await self._update(user)

        return True
