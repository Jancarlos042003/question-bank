from enum import IntEnum
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.helpers.subject_code import SubjectCode
from app.schemas.choice import ChoiceCreate, ChoiceRead
from app.schemas.solution import SolutionCreate, SolutionRead
from app.schemas.statement import (
    MatchingStatementCreate,
    StatementCreate,
    StatementRead,
    StatementWithItemsCreate,
    StatementWithoutItemsCreate,
)


class QuestionType(IntEnum):
    DIRECT = 1
    TRUE_FALSE = 2
    MATCHING = 3
    ORDERING = 4
    COMPLETION = 5


class QuestionBase(BaseModel):
    topic_id: int
    assessment_id: int
    question_number: Annotated[int | None, Field(default=None, gt=0)]


class QuestionCreate(QuestionBase):
    subject: SubjectCode
    solution: SolutionCreate
    statement: StatementCreate
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
                expected_type = StatementWithoutItemsCreate
            case QuestionType.TRUE_FALSE | QuestionType.ORDERING:
                expected_type = StatementWithItemsCreate
            case QuestionType.MATCHING:
                expected_type = MatchingStatementCreate
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
    solution: SolutionRead
    statement: StatementRead
    choices: List[ChoiceRead]

    model_config = ConfigDict(from_attributes=True)
