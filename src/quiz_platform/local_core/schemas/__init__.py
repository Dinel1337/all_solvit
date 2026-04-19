"""Pydantic схемы для Quiz Platform.

Create (Request):
- QuizCreate — создание квиза с вопросами и опциями
- AttemptCreate — начало попытки
- AnswerItem / AnswersBulkCreate — массовое сохранение ответов
- Publish — смена статуса (draft/published)

Response:
- QuizResponse — квиз с вопросами и опциями
- AttemptResponse — попытка с результатами
- UserAnswerResponse — ответ пользователя
- QuizFilters — пагинация и поиск
"""

from .create import (
    QuizCreate,
    AttemptCreate,
    AnswerItem,
    AnswersBulkCreate,
    QuestionCreate,
    AnswerOptionCreate
)
from .response import (
    QuizResponse,
    AttemptResponse,
    UserAnswerResponse,
    QuizFilters,
    ORMBaseModel,
    QuestionResponse,
    AnswerOptionResponse,
    Publish
)

__all__ = [
    'QuizCreate',
    'AttemptCreate',
    'AnswerItem',
    'AnswersBulkCreate',
    'QuestionCreate',
    'AnswerOptionCreate',
    'QuizResponse',
    'AttemptResponse',
    'UserAnswerResponse',
    'QuizFilters',
    'ORMBaseModel',
]