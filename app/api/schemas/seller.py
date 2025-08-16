from pydantic import BaseModel, EmailStr


class SellerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class SellerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr