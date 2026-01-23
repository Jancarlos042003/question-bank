from pydantic import BaseModel, Field, model_validator
from typing import Annotated, List, Literal


class StatementItem(BaseModel):
    id: Annotated[
        str, Field(description="Identificador del ítem (I, II, III o A, B, C)")
    ]
    content: Annotated[str, Field(description="Contenido del ítem")]


class StatementBase(BaseModel):
    text: Annotated[str, Field(..., description="Enunciado principal de la pregunta")]


# ============================================================================
# MODELOS PARA CREATE (sin image_paths)
# ============================================================================


class StatementWithItemsCreate(StatementBase):
    """Enunciado usado por: True/False, Ordering"""

    type: Literal["standard_with_items"] = "standard_with_items"
    items: Annotated[
        List[StatementItem],
        Field(
            min_length=2,
            max_length=5,
            description="Lista de ítems asociados al enunciado",
        ),
    ]


class StatementWithoutItemsCreate(StatementBase):
    """Enunciado usado por: Direct, Completion"""

    type: Literal["standard_without_items"] = "standard_without_items"


class MatchingStatementCreate(StatementBase):
    """Pregunta de relacionar columnas"""

    type: Literal["matching"] = "matching"
    left_column: Annotated[
        List[StatementItem],
        Field(
            max_length=5,
            description="Columna izquierda con items",
            examples=[
                [
                    {"id": "1", "content": "Mitocondria"},
                    {"id": "2", "content": "Ribosoma"},
                ]
            ],
        ),
    ]
    right_column: Annotated[
        List[StatementItem],
        Field(
            max_length=5,
            description="Columna derecha con items",
            examples=[
                [
                    {"id": "A", "content": "Síntesis de proteínas"},
                    {"id": "B", "content": "Producción de ATP"},
                ]
            ],
        ),
    ]

    @model_validator(mode="after")
    def validate_same_length(self):
        if len(self.left_column) != len(self.right_column):
            raise ValueError(
                "Las columnas izquierda y derecha deben tener la misma cantidad de ítems"
            )
        return self


# ============================================================================
# MODELOS PARA READ (con image_paths)
# ============================================================================


class StatementWithItemsRead(StatementWithItemsCreate):
    image_paths: List[str] | None = None


class StatementWithoutItemsRead(StatementWithoutItemsCreate):
    image_paths: List[str] | None = None


class MatchingStatementRead(MatchingStatementCreate):
    image_paths: List[str] | None = None


# ============================================================================
# UNIONES DISCRIMINADAS
# ============================================================================

StatementCreate = Annotated[
    StatementWithItemsCreate | StatementWithoutItemsCreate | MatchingStatementCreate,
    Field(discriminator="type"),
]

StatementRead = Annotated[
    StatementWithItemsRead | StatementWithoutItemsRead | MatchingStatementRead,
    Field(discriminator="type"),
]
