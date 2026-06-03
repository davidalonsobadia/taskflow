from typing import Generic, List, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class UserTokenPayload(BaseModel):
    user_id: int
    role: str

class PageMeta(BaseModel):
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    meta: PageMeta