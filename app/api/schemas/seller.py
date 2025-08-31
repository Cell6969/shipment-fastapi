from uuid import UUID
from pydantic import BaseModel, EmailStr


class SellerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class SellerResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr