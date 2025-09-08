import asyncio
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.config import notification_settings


fastmail = FastMail(ConnectionConfig(**notification_settings.model_dump()))


async def send_message():
    await fastmail.send_message(
        message=MessageSchema(
            recipients=["test@gmail.com"],
            subject="Test",
            body="Test",
            subtype=MessageType.plain,
        )
    )

    print("Message sent")


asyncio.run(send_message())
