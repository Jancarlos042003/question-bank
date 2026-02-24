import math
from typing import TypeVar

T = TypeVar("T")


def build_paginated_response(items: list[T], total: int, page: int, limit: int):
    pages = math.ceil(total / limit) if total > 0 else 1
    return {
        "data": items,
        "meta": {"page": page, "size": len(items), "total": total, "pages": pages},
    }
