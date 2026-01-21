from enum import IntEnum
from typing import Annotated, List, Literal

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

from app.schemas.choice import ChoiceCreate, ChoiceRead


class QuestionType(IntEnum):
    DIRECT = 1
    TRUE_FALSE = 2
    MATCHING = 3
    ORDERING = 4
    COMPLETION = 5


class StatementItem(BaseModel):
    id: Annotated[
        str, Field(description="Identificador del ítem (I, II, III o A, B, C)")
    ]
    content: Annotated[str, Field(description="Contenido del ítem")]


class StatementBase(BaseModel):
    text: Annotated[str, Field(..., description="Enunciado principal de la pregunta")]
    image_urls: Annotated[List[str] | None, Field(description="URLs de imágenes")] = (
        None
    )


class StatementWithItems(StatementBase):
    """
    Enunciado usado por:
    - True/False
    - Ordering
    """

    type: Literal["standard_with_items"] = "standard_with_items"
    items: Annotated[
        List[StatementItem],
        Field(
            min_length=2,
            max_length=5,
            description="Lista de ítems asociados al enunciado",
        ),
    ]


class StatementWithoutItems(StatementBase):
    """
    Enunciado usado por:
    - Direct
    - Completion
    """

    type: Literal["standard_without_items"] = "standard_without_items"


class MatchingStatement(StatementBase):
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


# Union discriminada
Statement = Annotated[
    StatementWithItems | StatementWithoutItems | MatchingStatement,
    Field(discriminator="type"),
]


class Solution(BaseModel):
    explanation: Annotated[
        str, Field(description="Explicación detallada de la solución")
    ]
    image_urls: List[str] | None = None


class QuestionBase(BaseModel):
    topic_id: int
    assessment_id: int
    question_number: Annotated[int | None, Field(default=None, gt=0)]
    statement: Statement
    solution: Solution


class QuestionCreate(QuestionBase):
    question_type_id: Annotated[
        QuestionType,
        Field(
            description="Tipo de pregunta (1=Directa, 2=Verdadero/Falso, 3=Relacionar, 4=Ordenamiento, 5=Completación"
        ),
    ]
    choices: Annotated[
        List[ChoiceCreate], Field(min_length=4, max_length=5, default_factory=list)
    ]

    @field_validator("choices")
    @classmethod
    def validate_single_correct(cls, choices: List[ChoiceCreate]):
        """Valida que exista exactamente una alternativa marcada como correcta (true)."""
        correct = sum(1 for c in choices if c.is_correct)

        if correct != 1:
            raise ValueError("Debe existir exactamente una alternativa correcta")

        return choices

    @field_validator("choices")
    @classmethod
    def validate_unique_responses(cls, choices: List[ChoiceCreate]):
        """Valida que el contenido de las alternativas sea único."""
        unique_choices = set()

        for c in choices:
            normalized = c.content.strip().lower()

            if normalized in unique_choices:
                raise ValueError("Las repuestas deben ser únicas")

            unique_choices.add(normalized)

        return choices

    @model_validator(mode="after")
    def validate_statement_type_consistency(self):
        """Valida que el tipo de statement coincida con `type_question_id`"""
        statement = self.statement
        type_id = self.question_type_id

        match type_id:
            case QuestionType.DIRECT | QuestionType.COMPLETION:
                expected_type = StatementWithoutItems
            case QuestionType.TRUE_FALSE | QuestionType.ORDERING:
                expected_type = StatementWithItems
            case QuestionType.MATCHING:
                expected_type = MatchingStatement
            case _:
                raise ValueError(f"Tipo de pregunta desconocido: {type_id}")

        if not isinstance(statement, expected_type):
            raise ValueError(
                f"Las preguntas de tipo {type_id.name} deben usar "
                f"{expected_type.__name__}, pero se recibió {type(statement).__name__}"
            )

        return self


class QuestionRead(QuestionBase):
    id: int
    question_hash: str
    question_type_id: int
    choices: List[ChoiceRead]

    model_config = ConfigDict(from_attributes=True)
