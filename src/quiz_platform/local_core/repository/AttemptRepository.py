from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Literal, Type
from datetime import datetime
from uuid import uuid4

from src._core.repositories.main_repository import BaseRepository
from src._core import RaiseControl
from src._core.exceptions import NotFoundError
from ..models.quiz_model import Attempt, UserAnswer, Quiz, Question, AnswerOption
from ..exceptions import AttemptNotFoundError, QuizNotFoundError

_ExcMeta = Literal['attempt', 'quiz']
_error_map: Dict[_ExcMeta, Type[NotFoundError]] = {
    "attempt": AttemptNotFoundError,
    "quiz": QuizNotFoundError,
}
_model_error_map = {
    Attempt: AttemptNotFoundError,
    Quiz: QuizNotFoundError,
}

RControl = RaiseControl(_error_map, _model_error_map, default_error=AttemptNotFoundError)


class AttemptRepository(BaseRepository[Attempt]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Attempt)
        self.user_answer_repo = UserAnswerRepository(session)


    async def create_attempt(
        self,
        quiz_id: int,
        user_id: Optional[int] = None,
        anonymous_token: Optional[str] = None
    ) -> Attempt:
        """Создаёт новую попытку прохождения викторины."""
        if not anonymous_token and user_id is None:
            anonymous_token = str(uuid4())

        attempt_data = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "anonymous_token": anonymous_token,
            "started_at": datetime.now(),
            "finished_at": None,
            "total_score": 0,
        }

        attempt_data = {k: v for k, v in attempt_data.items() if v is not None}
        return await self.create(data=attempt_data, commit=True)

    @RControl(exc='attempt', param_pos=1)
    async def get_attempt_with_details(self, attempt_id: int) -> Attempt:
        """
        Возвращает попытку с подгруженными:
        - вопросами квиза
        - вариантами ответов
        - уже сохранёнными ответами пользователя
        """
        stmt = (
            select(Attempt)
            .where(Attempt.id == attempt_id)
            .options(
                selectinload(Attempt.quiz).selectinload(Quiz.questions).selectinload(Question.options),
                selectinload(Attempt.user_answers).selectinload(UserAnswer.selected_option),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    @RControl(exc='attempt', param_pos=1)
    async def get_attempt_by_id(self, attempt_id: int) -> Attempt:
        """Просто получить попытку без подгрузок (быстро)."""
        return await self.find_one_by(id=attempt_id)

    async def finish_attempt(self, attempt_id: int, total_score: int) -> bool:
        """Завершает попытку: проставляет finished_at и total_score."""
        stmt = (
            update(Attempt)
            .where(Attempt.id == attempt_id, Attempt.finished_at.is_(None))
            .values(finished_at=datetime.now(), total_score=total_score)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0

    async def save_or_update_answer(self, attempt_id: int, question_id: int, selected_option_id: int) -> UserAnswer:
        return await self.user_answer_repo.save_or_update_answer(attempt_id, question_id, selected_option_id)
    
    async def get_user_answers_for_attempt(self, attempt_id: int) -> List[UserAnswer]:
        return await self.user_answer_repo.get_user_answers_for_attempt(attempt_id)

    async def is_attempt_finished(self, attempt_id: int) -> bool:
        """Проверяет, завершена ли попытка."""
        finished_at = await self.find_scalar_by(
            column=Attempt.finished_at,
            id=attempt_id
        )
        return finished_at is not None
    
    async def is_question_belongs_to_quiz(self, question_id: int, quiz_id: int) -> bool:
        """Проверяет, принадлежит ли вопрос указанному квизу."""
        stmt = select(Question).where(Question.id == question_id, Question.quiz_id == quiz_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def is_option_belongs_to_question(self, option_id: int, question_id: int) -> bool:
        """Проверяет, принадлежит ли вариант ответа указанному вопросу."""
        stmt = select(AnswerOption).where(AnswerOption.id == option_id, AnswerOption.question_id == question_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None


class UserAnswerRepository(BaseRepository[UserAnswer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserAnswer)
    
    async def save_or_update_answer(
        self,
        attempt_id: int,
        question_id: int,
        selected_option_id: int
    ) -> UserAnswer:
        existing = await self.find_one_by(
            attempt_id=attempt_id,
            question_id=question_id
        )
        if existing:
            existing.selected_option_id = selected_option_id
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
            return await self.create(
                data={
                    "attempt_id": attempt_id,
                    "question_id": question_id,
                    "selected_option_id": selected_option_id,
                },
                commit=True
            )
    # @RaiseControl
    async def get_user_answers_for_attempt(self, attempt_id: int) -> List[UserAnswer]:
        stmt = (
            select(UserAnswer)
            .where(UserAnswer.attempt_id == attempt_id)
            .options(
                selectinload(UserAnswer.question),
                selectinload(UserAnswer.selected_option),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()