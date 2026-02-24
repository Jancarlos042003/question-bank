from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

T = TypeVar("T")  # data
M = TypeVar("M", default=BaseModel)  # meta


class ApiResponse(GenericModel, Generic[T, M]):
    data: T
    meta: M | None = None

    model_config = ConfigDict(from_attributes=True)
