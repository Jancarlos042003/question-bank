from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class PaginatedResult(Generic[T]):
    total_count: int
    total_pages: int
    current_page: int
    items_count: int
    has_prev: bool
    has_next: bool
    items: list[T]
