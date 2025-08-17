from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class Pagination(BaseModel):
    page: int
    size: int
    total_data:int

class ApiResponse(BaseModel, Generic[T]):
    status_code:int
    message:str
    data:T
    pagination: Optional[Pagination] = None

    @staticmethod
    def success(message:str,data: T, pagination:Optional[Pagination] = None):
        return ApiResponse(status_code=200, message=message, data=data, pagination=pagination)
