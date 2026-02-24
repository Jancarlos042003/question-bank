from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel


class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
    pages: int

    model_config = ConfigDict(from_attributes=True)
