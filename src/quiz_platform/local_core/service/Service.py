from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Any, Literal, List
from uuid import uuid4

from src._core.exceptions import NotOwnerError
from src._core.database import get_db
from src._core.services import LoggerService
from ..models.quiz_model import Quiz, Attempt, UserAnswer
from ..repository import QuizRepository, QuestionRepository, AttemptRepository
from ..schemas import QuizCreate, AnswerItem
from ..exceptions import AttemptAlreadyFinishedError,QuizNotPublishedError


async def get_quiz_service(
    db: AsyncSession = Depends(get_db)
) -> "QuizService":
    """DI для QuizService"""
    return QuizService(
        QuizRepository(db),
        QuestionRepository(db),
        AttemptRepository(db)
    )


class QuizService(LoggerService):
    """Сервис для работы с викторинами и попытками"""

    def __init__(
        self,
        repository: QuizRepository,
        question_repository: Optional[QuestionRepository] = None,
        attempt_repository: Optional[AttemptRepository] = None,
    ) -> None:
        self.repository: QuizRepository = repository
        self.question_repo: Optional[QuestionRepository] = question_repository
        self.attempt_repo: Optional[AttemptRepository] = attempt_repository
        super().__init__()

    async def create_quiz(self, data: QuizCreate, user_id: int) -> Quiz:
        """Создание викторины с вопросами и ответами"""
        try:
            result = await self.repository.create_quiz(data, user_id)
            self.logger.info(f"Создан квиз: {result.id} для пользователя {user_id}")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка создания квиза: {e}")
            raise

    async def get_quiz(self, search_param: Any, search_field: Literal['id', 'name'] = None, simple: bool = None) -> Quiz:
        """Получение викторины по ID или имени"""
        try:
            if search_field is None:
                search_field = "id" if isinstance(search_param, int) else "name"

            if search_field == "id":
                quiz = await self.repository.get_by_id(search_param, simple)
            else:
                quiz = await self.repository.get_by_name_z(search_param, simple)

            self.logger.info(f"Получен квиз: {quiz.id} ({quiz.name})")
            return quiz
        except Exception as e:
            self.logger.error(f"Ошибка получения квиза по полю '{search_field}' со значением '{search_param}': {e}")
            raise

    async def get_quizzes(
        self,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Quiz]:
        """Получение списка викторин с фильтрацией"""
        try:
            result = await self.repository.get_quizzes(search=search, limit=limit, offset=offset)
            self.logger.info(f"Получен список квизов: {len(result)} записей")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка получения списка квизов: {e}")
            raise

    async def set_publish(self,
                          publish: Literal['draft', 'published'],
                          quiz_id: int,
                          user_id: int):
        """Изменить статус викторины (опубликовать/снять)"""
        result = await self.get_quiz(search_param=quiz_id, simple=True)
        if user_id != result.author_id:
            raise NotOwnerError('Викторины', 'Доступ запрещен')

        await self.repository.update_by_id(quiz_id, {
            'status': publish
        })

    async def start_attempt(
        self,
        quiz_id: int,
        user_id: Optional[int] = None,
        anonymous_token: Optional[str] = None
    ) -> Attempt:
        """
        Начать прохождение викторины.
        - Проверяет, что викторина опубликована.
        - Создаёт запись в Attempt.
        - Для неавторизованных генерирует anonymous_token.
        """
        quiz = await self.repository.get_by_id(quiz_id, simple=True)
        if quiz.status != "published":
            raise QuizNotPublishedError(quiz_id)

        if not user_id and not anonymous_token:
            anonymous_token = str(uuid4())

        attempt = await self.attempt_repo.create_attempt(
            quiz_id=quiz_id,
            user_id=user_id,
            anonymous_token=anonymous_token
        )
        self.logger.info(f"Создана попытка {attempt.id} для квиза {quiz_id}")
        return attempt

    async def save_answers_bulk(
        self,
        attempt_id: int,
        answers_data: List[AnswerItem]
    ) -> List[UserAnswer]:
        """
        Массовое сохранение ответов пользователя.
        """
        attempt = await self.attempt_repo.get_attempt_by_id(attempt_id)
        if attempt.finished_at is not None:
            raise AttemptAlreadyFinishedError(attempt_id)

        saved_answers = []
        errors = []

        for item in answers_data:
            question_id = item.question_id 
            selected_option_id = item.selected_option_id

            try:
                if not await self.attempt_repo.is_question_belongs_to_quiz(question_id, attempt.quiz_id):
                    errors.append({"question_id": question_id, "error": "Question not in quiz"})
                    continue

                if not await self.attempt_repo.is_option_belongs_to_question(selected_option_id, question_id):
                    errors.append({"question_id": question_id, "error": "Option not belongs to question"})
                    continue
                
                user_answer = await self.attempt_repo.save_or_update_answer(
                    attempt_id=attempt_id,
                    question_id=question_id,
                    selected_option_id=selected_option_id
                )
                saved_answers.append(user_answer)
            except Exception as e:
                errors.append({"question_id": question_id, "error": str(e)})

        self.logger.info(f"Сохранено {len(saved_answers)} ответов для попытки {attempt_id}, ошибок: {len(errors)}")
        if errors:
            self.logger.warning(f"Ошибки: {errors}")
        return saved_answers

    async def finish_attempt(self, attempt_id: int) -> int:
        """
        Завершить попытку: подсчитать баллы и обновить запись.
        Возвращает итоговый балл.
        """
        attempt = await self.attempt_repo.get_attempt_by_id(attempt_id)
        if attempt.finished_at is not None:
            raise AttemptAlreadyFinishedError(attempt_id)

        answers = await self.attempt_repo.get_user_answers_for_attempt(attempt_id)

        total_score = 0
        for ans in answers:
            if ans.selected_option and ans.selected_option.is_correct:
                total_score += ans.question.points

        await self.attempt_repo.finish_attempt(attempt_id, total_score)

        self.logger.info(f"Попытка {attempt_id} завершена. Баллы: {total_score}")
        return total_score

    async def get_attempt_result(self, attempt_id: int) -> dict:
        """
        Получить детальный результат прохождения:
        - информация о квизе
        - общий балл / максимальный балл
        - ответы на каждый вопрос с указанием правильности
        """
        attempt = await self.attempt_repo.get_attempt_with_details(attempt_id)

        quiz = attempt.quiz
        questions = quiz.questions

        max_score = sum(q.points for q in questions)

        user_answers_map = {ua.question_id: ua for ua in attempt.user_answers}

        details = []
        for q in questions:
            user_ans = user_answers_map.get(q.id)
            selected_option_id = user_ans.selected_option_id if user_ans else None
            is_correct = False
            if selected_option_id:
                opt = next((o for o in q.options if o.id == selected_option_id), None)
                is_correct = opt.is_correct if opt else False

            details.append({
                "question_id": q.id,
                "question_text": q.text,
                "points": q.points,
                "selected_option_id": selected_option_id,
                "is_correct": is_correct,
                "earned_points": q.points if is_correct else 0
            })

        return {
            "attempt_id": attempt.id,
            "quiz_id": quiz.id,
            "quiz_name": quiz.name,
            "started_at": attempt.started_at.isoformat() if attempt.started_at else None,
            "finished_at": attempt.finished_at.isoformat() if attempt.finished_at else None,
            "total_score": attempt.total_score,
            "max_possible_score": max_score,
            "answers": details
        }
        
