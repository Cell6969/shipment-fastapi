from fastapi.background import BackgroundTasks
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr
from app.config import notification_settings


class NotificationService:
    def __init__(self, tasks: BackgroundTasks) -> None:
        self.fastmail = FastMail(ConnectionConfig(**notification_settings.model_dump()))
        self.tasks = tasks

    async def send_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        body: str,
    ):
        self.tasks.add_task(
            self.fastmail.send_message,
            message=MessageSchema(
                recipients=recipients,
                subject=subject,
                body=body,
                subtype=MessageType.plain,
            ),
        )
