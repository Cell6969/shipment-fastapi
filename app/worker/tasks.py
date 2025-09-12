from celery import Celery
from pydantic import EmailStr
from app.config import db_settings, notification_settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from twilio.rest import Client
from asgiref.sync import async_to_sync
from app.utils import TEMPLATE_DIR

fastmail = FastMail(
    ConnectionConfig(
        **notification_settings.model_dump(
            exclude={"TWILIO_AUTH_TOKEN", "TWILIO_SID", "TWILIO_PHONE_NUMBER"}
        ),
        TEMPLATE_FOLDER=TEMPLATE_DIR
    )
)

twilio_client = Client(
    notification_settings.TWILIO_SID,
    notification_settings.TWILIO_AUTH_TOKEN,
)

send_message = async_to_sync(fastmail.send_message)


app = Celery(
    "api_task",
    broker=db_settings.get_redis_url(9),
    backend=db_settings.get_redis_url(9),
)


@app.task
def send_mail(
    recipients: list[str],
    subject: str,
    body: str,
):
    send_message(
        message=MessageSchema(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=MessageType.plain,
        )
    )

    return "message sent"


@app.task
def send_email_with_template(
    recipients: list[EmailStr],
    subject: str,
    context: dict,
    template_name: str,
):
    send_message(
        message=MessageSchema(
            recipients=recipients,
            subject=subject,
            template_body=context,
            subtype=MessageType.html,
        ),
        template_name=template_name,
    )


@app.task
def send_sms(to: str, body: str):
    twilio_client.messages.create(
        body=body,
        from_=notification_settings.TWILIO_PHONE_NUMBER,
        to=to,
    )

@app.task
def add_log(log:str) -> None:
    with open("file.log", 'a') as file:
        file.write(f"{log}\n")