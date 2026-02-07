from enum import IntEnum
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.v1.area.schemas import AreaResponse
from app.api.v1.choice.schemas import ChoiceCreateInput, ChoiceResponse
from app.api.v1.difficulty.schemas import DifficultyResponse
from app.api.v1.question_content.schemas import (
    QuestionContentCreateInput,
    QuestionContentResponse,
)
from app.api.v1.question_type.schemas import QuestionTypeRead
from app.api.v1.solution.schemas import SolutionCreateInput, SolutionResponse
from app.api.v1.solution_content.shemas import SolutionContentResponse
from app.api.v1.subtopic.schemas import SubtopicResponse
from app.helpers.subject_code import SubjectCode


class QuestionType(IntEnum):
    DIRECT = 1
    TRUE_FALSE = 2
    MATCHING = 3
    ORDERING = 4
    COMPLETION = 5


class QuestionBase(BaseModel):
    question_type_id: Annotated[
        QuestionType,
        Field(
            description="Tipo de pregunta",
            examples=[
                "1=Directa",
                "2=Verdadero/Falso",
                "3=Relacionar",
                "4=Ordenamiento",
                "5=Completación",
            ],
        ),
    ]
    subtopic_id: int
    difficulty_id: int


class QuestionCreate(QuestionBase):
    question_hash: Annotated[str, Field(description="Hash de la pregunta")]


class QuestionCreateInput(QuestionBase):
    area_ids: Annotated[
        List[int],
        Field(
            min_length=1,
            description="Lista de IDs de áreas válidas",
            examples=["1=A", "2=B", "3=C", "4=D", "5=E"],
            default_factory=list,
        ),
    ]
    # subject: SubjectCode OJO: VER SI ES NECESARIO para almacenar las imágenes
    contents: Annotated[
        List[QuestionContentCreateInput],
        Field(description="Contenido de la pregunta", default_factory=list),
    ]
    solution: Annotated[
        SolutionCreateInput, Field(description="Solución de la pregunta")
    ]
    choices: Annotated[
        List[ChoiceCreateInput], Field(min_length=4, max_length=5, default_factory=list)
    ]

    @field_validator("choices")
    @classmethod
    def validate_single_correct(cls, choices: List[ChoiceCreateInput]):
        """Valida que exista exactamente una alternativa marcada como correcta (true)."""
        correct = sum(1 for c in choices if c.is_correct)

        if correct != 1:
            raise ValueError("Debe existir exactamente una alternativa correcta")

        return choices

    @field_validator("choices")
    @classmethod
    def validate_unique_responses(cls, choices: List[ChoiceCreateInput]):
        """Valida que el contenido de las alternativas sea único."""
        unique_choices = set()

        for c in choices:
            for content in c.contents:
                normalized = content.value.strip().lower()

                if normalized in unique_choices:
                    raise ValueError("Las respuestas deben ser únicas")

                unique_choices.add(normalized)

        return choices


# Para estudio / banco
class QuestionStudyResponse(BaseModel):
    id: int
    question_hash: Annotated[str, Field(description="Hash de la pregunta")]
    question_type: QuestionTypeRead
    subtopic: SubtopicResponse
    difficulty: DifficultyResponse
    areas: List[AreaResponse]
    choices: List[ChoiceResponse]
    solution: SolutionResponse

    model_config = ConfigDict(from_attributes=True)


# Para simulacros exámenes
class QuestionSolveResponse(BaseModel):
    id: int
    question_hash: str
    contents: List[QuestionContentResponse]
    choices: List[ChoiceResponse]

    model_config = ConfigDict(from_attributes=True)
