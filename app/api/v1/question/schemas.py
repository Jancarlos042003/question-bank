from enum import IntEnum
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.v1.choice.schemas import ChoiceCreateInput, ChoicePublic
from app.api.v1.difficulty.schemas import DifficultyPublic
from app.api.v1.question_content.schemas import (
    QuestionContentCreateInput,
    QuestionContentResponse,
)
from app.api.v1.question_source.schemas import (
    QuestionSourceCreateInput,
    QuestionSourcePublic,
)
from app.api.v1.question_type.schemas import QuestionTypeCodeOnly
from app.api.v1.solution.schemas import SolutionCreateInput, SolutionPublic
from app.api.v1.subtopic.schemas import SubtopicSimplePublic
from app.core.exceptions.domain import (
    DuplicateChoiceContentError,
    MultipleCorrectChoicesError,
    NoCorrectChoiceError,
)


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
            examples=[1],
        ),
    ]
    subtopic_id: int
    difficulty_id: int


# PRIVADO
class QuestionCreate(QuestionBase):
    question_hash: Annotated[str, Field(description="Hash de la pregunta")]


class QuestionCreateInput(QuestionBase):
    area_ids: Annotated[
        List[int],
        Field(
            min_length=1,
            description="Lista de IDs de áreas válidas",
            examples=[1, 2, 3, 4, 5],
            default_factory=list,
        ),
    ]
    # subject: SubjectCode OJO: VER SI ES NECESARIO para almacenar las imágenes
    contents: Annotated[
        List[QuestionContentCreateInput],
        Field(description="Contenido de la pregunta", default_factory=list),
    ]
    solutions: Annotated[
        list[SolutionCreateInput], Field(description="Soluciones de la pregunta")
    ]
    choices: Annotated[
        List[ChoiceCreateInput], Field(min_length=4, max_length=5, default_factory=list)
    ]
    sources: Annotated[
        List[QuestionSourceCreateInput],
        Field(
            min_length=1,
            description="Lista de fuentes asociadas a la pregunta",
            default_factory=list,
        ),
    ]

    @field_validator("choices")
    @classmethod
    def validate_single_correct(cls, choices: List[ChoiceCreateInput]):
        """
        Valida que exista exactamente una alternativa marcada como correcta (true).
        """
        correct = sum(1 for c in choices if c.is_correct)

        if correct == 0:
            raise NoCorrectChoiceError("Debe existir al menos una alternativa correcta")
        elif correct > 1:
            raise MultipleCorrectChoicesError(
                "Debe existir exactamente una alternativa correcta"
            )

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
                    message = (
                        "Las respuestas deben ser únicas. "
                        f"Contenido duplicado: '{normalized}'"
                    )
                    raise DuplicateChoiceContentError(
                        message
                    )

                unique_choices.add(normalized)

        return choices


class QuestionTypeSpecificUpdate(BaseModel):
    question_type_id: Annotated[
        QuestionType,
        Field(description="Tipo de pregunta", examples=[1]),
    ]


class QuestionSubtopicSpecificUpdate(BaseModel):
    subtopic_id: Annotated[
        int,
        Field(gt=0, description="ID del subtema", examples=[1]),
    ]


class QuestionDifficultySpecificUpdate(BaseModel):
    difficulty_id: Annotated[
        int,
        Field(gt=0, description="ID de la dificultad", examples=[1]),
    ]


class QuestionAreasSpecificUpdate(BaseModel):
    area_ids: Annotated[
        List[int],
        Field(
            min_length=1,
            description="Lista de IDs de áreas válidas",
            examples=[1, 2],
        ),
    ]


class QuestionAreasSectionResponse(BaseModel):
    id: int
    areas: list[str]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("areas", mode="before")
    @classmethod
    def flatten_areas(cls, v):
        if v is None:
            return []

        out: list[str] = []
        for item in v:
            if hasattr(item, "code"):
                out.append(item.code)
                continue

            out.append(str(item))
        return out


# PÚBLICO
# Para estudio / banco
class QuestionCreateResponse(BaseModel):
    id: int
    question_type: QuestionTypeCodeOnly
    subtopic: SubtopicSimplePublic
    difficulty: DifficultyPublic
    areas: list[str]
    contents: list[QuestionContentResponse]
    choices: list[ChoicePublic]
    solutions: list[SolutionPublic]
    sources: Annotated[
        list[QuestionSourcePublic],
        Field(
            validation_alias="question_sources",
            description="Fuentes asociadas a la pregunta",
        ),
    ]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("areas", mode="before")
    @classmethod
    def flatten_areas(cls, v):
        """
        Su función principal es aplanar y normalizar la lista de áreas (list[Area ORM])
        asociadas a una pregunta y devolver list[str] (ej. ["A", "B", "C"]).
        """
        if v is None:
            return []

        out: list[str] = []
        for item in v:
            # Verificar si el atributo 'code' existe
            if hasattr(item, "code"):
                out.append(item.code)
                continue

            # fallback
            out.append(str(item))
        return out


class QuestionSummaryPublic(BaseModel):
    id: int
    contents: list[QuestionContentResponse]
    difficulty: DifficultyPublic
    areas: list[str]
    subtopic: SubtopicSimplePublic
    sources: Annotated[
        list[QuestionSourcePublic],
        Field(
            validation_alias="question_sources",
            description="Fuentes asociadas a la pregunta",
        ),
    ]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("areas", mode="before")
    @classmethod
    def flatten_areas(cls, v):
        if v is None:
            return []

        out: list[str] = []
        for item in v:
            if hasattr(item, "code"):
                out.append(item.code)
                continue

            out.append(str(item))
        return out


class QuestionDetailPublic(BaseModel):
    id: int
    contents: list[QuestionContentResponse]
    difficulty: DifficultyPublic
    areas: list[str]
    subtopic: SubtopicSimplePublic
    choices: list[ChoicePublic]
    solutions: list[SolutionPublic]
    sources: Annotated[
        list[QuestionSourcePublic],
        Field(
            validation_alias="question_sources",
            description="Fuentes asociadas a la pregunta",
        ),
    ]

    model_config = ConfigDict(from_attributes=True)

    @field_validator("areas", mode="before")
    @classmethod
    def flatten_areas(cls, v):
        if v is None:
            return []

        out: list[str] = []
        for item in v:
            if hasattr(item, "code"):
                out.append(item.code)
                continue

            out.append(str(item))
        return out


class QuestionPaginatedSummaryResponse(BaseModel):
    total_count: int
    total_pages: int
    current_page: int
    items_count: int
    has_prev: bool
    has_next: bool
    items: list[QuestionSummaryPublic]
    model_config = ConfigDict(from_attributes=True)


class QuestionPaginatedDetailResponse(BaseModel):
    total_count: int
    total_pages: int
    current_page: int
    items_count: int
    has_prev: bool
    has_next: bool
    items: list[QuestionDetailPublic]
    model_config = ConfigDict(from_attributes=True)


# Para simulacros exámenes
class QuestionSolveResponse(BaseModel):
    id: int
    question_hash: str
    contents: List[QuestionContentResponse]
    choices: List[ChoicePublic]

    model_config = ConfigDict(from_attributes=True)
