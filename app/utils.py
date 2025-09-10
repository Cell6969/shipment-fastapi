from datetime import timedelta, datetime, timezone
from pathlib import Path
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, encode, decode, PyJWTError
from app.config import security_settings as settings
from uuid import uuid4
from itsdangerous import (
    BadSignature,
    Serializer,
    SignatureExpired,
    URLSafeTimedSerializer,
)

# Directory
APP_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = APP_DIR / "templates"

# serializer encode token
_serializer = URLSafeTimedSerializer(settings.JWT_SECRET)


# Method utils
def generate_access_token(data: dict, expiry: timedelta = timedelta(days=1)) -> str:
    return encode(
        payload={
            **data,
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + expiry,
        },
        algorithm=settings.JWT_ALGORITHM,
        key=settings.JWT_SECRET,
    )


def decode_access_token(token: str) -> dict | None:
    try:
        return decode(
            jwt=token, key=settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )

    except PyJWTError:
        return None


def generate_url_safe_token(data: dict) -> str:
    return _serializer.dumps(data)


def decode_url_safe_token(token: str, expiry: timedelta | None = None) -> dict | None:
    try:
        return (
            _serializer.loads(token, max_age=int(expiry.total_seconds()))
            if expiry
            else _serializer.loads(token)
        )
    except (BadSignature, SignatureExpired):
        return None
