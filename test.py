import asyncio
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.config import notification_settings
from twilio.rest import Client

fastmail = FastMail(ConnectionConfig(**notification_settings.model_dump(include={'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_PORT', 'MAIL_SERVER', 'MAIL_TLS', 'MAIL_SSL', 'USE_CREDENTIALS', 'VALIDATE_CERTS', 'MAIL_STARTTLS', 'MAIL_SSL_TLS', 'MAIL_FROM'})))
client = Client(
    notification_settings.TWILIO_SID,
    notification_settings.TWILIO_AUTH_TOKEN,
)


async def send_message():
    await fastmail.send_message(
        message=MessageSchema(
            recipients=["test@gmail.com"],
            subject="Test",
            body="Test",
            subtype=MessageType.plain,
        )
    )

    # client.messages.create(
    #     body="Test",
    #     from_=notification_settings.TWILIO_PHONE_NUMBER,
    #     to="+16673275027",
    # )

    print("Message sent")


asyncio.run(send_message())
