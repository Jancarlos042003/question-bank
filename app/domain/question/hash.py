import hashlib
from typing import Iterable, Protocol

from app.domain.content_type import ContentType


class QuestionHashContent(Protocol):
    type: ContentType
    value: str
    order: int


def generate_question_hash(contents: Iterable[QuestionHashContent]) -> str:
    ordered_contents = sorted(contents, key=lambda i: i.order)
    base = ""

    for item in ordered_contents:
        content_type = getattr(item.type, "value", item.type)
        if content_type == "image":
            break

        base += item.value.strip().lower()

    return hashlib.sha256(base.encode("utf-8")).hexdigest()
