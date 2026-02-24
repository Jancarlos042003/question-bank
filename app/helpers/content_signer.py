from typing import Any, Callable, Iterable, Protocol


class SignableContent(Protocol):
    type: Any
    value: str


def sign_image_contents(
        contents: Iterable[SignableContent],
        sign_storage_object_name: Callable[[str], str],
) -> None:
    for content in contents:
        content_type = getattr(content.type, "value", content.type)
        if content_type == "image":
            content.value = sign_storage_object_name(content.value)
