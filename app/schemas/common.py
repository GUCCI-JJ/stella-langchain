from enum import IntEnum
from typing import Generic, Optional, TypeVar, List

from pydantic import BaseModel

T = TypeVar('T')


class BizCode(IntEnum):
    OK = 200
    PARAM_ERROR = 400
    SERVER_ERROR = 500
    UNAUTHORIZED = 401
    NOT_FOUND = 404


class ApiResponse(BaseModel, Generic[T]):
    code: int=BizCode.OK
    data: Optional[T] = None
    message: str = 'ok'


class PageMeta(BaseModel, Generic[T]):
    page: int
    page_size: int
    total: int


class PageResponse(BaseModel, Generic[T]):
    rows: List[T]
    meta: PageMeta

