from math import ceil
from typing import Generic, List, Sequence, Tuple, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Query

from app.core.schemas import PageMeta, PaginatedResponse

T = TypeVar("T")


def paginate_query(query: Query, page: int, page_size: int) -> Tuple[Sequence, int]:
    """
    Execute a SQLAlchemy query with pagination and return (items, total_count).
    This function strips ordering for the count query for performance.
    """
    # Ensure valid bounds
    page = max(page, 1)
    page_size = max(page_size, 1)

    # Compute total count (ignore any ORDER BY for efficiency)
    total_count = query.order_by(None).count()

    # Apply pagination
    offset = (page - 1) * page_size
    items = query.limit(page_size).offset(offset).all()

    return items, total_count


def build_paginated_response(items: List[T], total_count: int, page: int, page_size: int) -> PaginatedResponse[T]:
    """Build a standard PaginatedResponse from items and total count."""
    page = max(page, 1)
    page_size = max(page_size, 1)

    if total_count <= 0:
        total_pages = 0
    else:
        total_pages = ceil(total_count / page_size)

    meta = PageMeta(
        page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1 and total_count > 0,
    )

    return PaginatedResponse[T](items=items, meta=meta)

