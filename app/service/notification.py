from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr
from app.config import notification_settings


class NotificationService:
    def __init__(self) -> None:
        self.fastmail = FastMail(ConnectionConfig(**notification_settings.model_dump()))

    async def send_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        body: str,
    ):
        await self.fastmail.send_message(
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                body=body,
                subtype=MessageType.plain,
            )
        )
