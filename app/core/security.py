from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer

from app.core.exception import InvalidToken
from app.utils import decode_access_token

oauth2_scheme_seller = OAuth2PasswordBearer(tokenUrl="/seller/token")
oauth2_scheme_partner = OAuth2PasswordBearer(tokenUrl="/partner/token")


class AccessTokenBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth_credentials = await super().__call__(request)

        if auth_credentials is None or not auth_credentials.credentials:
            raise InvalidToken()
        token_data = decode_access_token(auth_credentials.credentials)

        if token_data is None:
            raise InvalidToken()

        return token_data


access_token_bearer = AccessTokenBearer()
Annotated[dict, Depends(access_token_bearer)]
