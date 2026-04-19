"""Репозитории для Quiz Platform.

Используют RaiseControl для автоматической генерации 404.

- QuizRepository — CRUD квизов, поиск по id/name, пагинация, публикация
- QuestionRepository — создание вопросов и опций
- AttemptRepository — управление попытками, сохранение ответов, подсчёт баллов
"""

from .QuizRepository import QuizRepository, QuestionRepository
from .AttemptRepository import AttemptRepository

__all__ = [
    'QuizRepository',
    'QuestionRepository',
    'AttemptRepository',
]