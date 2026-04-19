"""Кастомные исключения для Quiz Platform.

Используются с RaiseControl для автоматической генерации 404.

- QuizNotFoundError — квиз не найден
- QuestionNotFoundError — вопрос не найден
- AnswerOptionNotFoundError — вариант ответа не найден
- AttemptNotFoundError — попытка не найдена
- UserAnswerNotFoundError — ответ пользователя не найден
- AttemptAlreadyFinishedError — попытка уже завершена
- QuizNotPublishedError — попытка пройти неопубликованный квиз
- InvalidAnswerError — ответ не принадлежит вопросу
"""

from .attempt import (
    AttemptNotFoundError,
    AttemptAlreadyFinishedError,
    QuizNotPublishedError,
    InvalidAnswerError,
)
from .quiz import (
    QuizNotFoundError,
    QuestionNotFoundError,
    AnswerOptionNotFoundError,
    UserAnswerNotFoundError,
)

__all__ = [
    'AttemptNotFoundError',
    'AttemptAlreadyFinishedError',
    'QuizNotPublishedError',
    'InvalidAnswerError',
    'QuizNotFoundError',
    'QuestionNotFoundError',
    'AnswerOptionNotFoundError',
    'UserAnswerNotFoundError',
]