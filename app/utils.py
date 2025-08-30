from datetime import timedelta, datetime, timezone
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, encode, decode, PyJWTError
from app.config import security_settings as settings


def generate_access_token(data: dict, expiry: timedelta = timedelta(days=1)) -> str:
    return encode(
        payload={
            **data,
            "exp": datetime.now(timezone.utc) + expiry,
        },
        algorithm=settings.JWT_ALGORITHM,
        key=settings.JWT_SECRET,
    )


def decode_access_token(token:str) -> dict | None:
    try:
        return decode(
            jwt=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
    except PyJWTError:
        return None
