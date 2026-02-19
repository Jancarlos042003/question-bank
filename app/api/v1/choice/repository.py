from sqlalchemy import func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.models.choice import Choice
from app.models.choice_content import ChoiceContent


class ChoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_choice_db(self, question_id: int, choice_id: int):
        """Obtiene una alternativa por ``question_id`` y ``choice_id``"""
        stmt = (
            select(Choice)
            .where(Choice.id == choice_id, Choice.question_id == question_id)
            .options(selectinload(Choice.contents))
        )
        return self.db.scalar(stmt)

    def count_correct_choices_db(
            self, question_id: int, exclude_choice_id: int | None = None
    ):
        """
        Cuenta las alternativas correctas de una pregunta, excluyendo opcionalmente
        una alternativa específica.
        """
        stmt = (
            select(func.count())
            .select_from(Choice)
            .where(Choice.question_id == question_id, Choice.is_correct.is_(True))
        )
        if exclude_choice_id is not None:
            # Excluir la alternativa especificada del conteo de repuestas correctas
            stmt = stmt.where(Choice.id != exclude_choice_id)

        return self.db.scalar(stmt) or 0

    def get_other_choice_content_values_db(self, question_id: int, choice_id: int):
        """
        Obtiene los valores normalizados de los contenidos de las demás alternativas de una pregunta,
        excluyendo ``choice_id``.
        """
        stmt = (
            select(ChoiceContent.value)
            .join(Choice, ChoiceContent.choice_id == Choice.id)
            .where(Choice.question_id == question_id, Choice.id != choice_id)
        )
        values = self.db.scalars(stmt).all()
        return {value.strip().lower() for value in values}

    def update_choice_db(
            self,
            choice: Choice,
            question_id: int,
            label: str | None,
            is_correct: bool | None,
            contents: list[ChoiceContent] | None,
            demote_others: bool,
    ):
        """
        Actualiza los campos de una alternativa en la base de datos.

        :param choice: Instancia de ``Choice`` a actualizar.
        :param question_id: ID de la pregunta a la que pertenece la alternativa.
        :param label: Nueva etiqueta de la alternativa.
        :param is_correct: Nuevo valor de corrección de la alternativa.
        :param contents: Nueva lista de contenidos de la alternativa.
        :param demote_others: Si es ``True``, marca como incorrectas las demás alternativas correctas
            de la misma pregunta antes de aplicar los cambios.
        :return: La instancia de ``Choice`` actualizada y refrescada desde la base de datos.
        :raises SQLAlchemyError: Si ocurre un error durante la transacción, se hace rollback y se
            relanza la excepción.
        """

        try:
            if demote_others:
                self.db.execute(
                    update(Choice)
                    .where(
                        Choice.question_id == question_id,
                        Choice.id != choice.id,
                        Choice.is_correct.is_(True),
                    )
                    .values(is_correct=False)
                )

            if label is not None:
                choice.label = label

            if is_correct is not None:
                choice.is_correct = is_correct

            if contents is not None:
                choice.contents = contents

            self.db.commit()
            self.db.refresh(choice)
            return choice
        except SQLAlchemyError:
            self.db.rollback()
            raise
