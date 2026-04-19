"""Сервисный слой для Quiz Platform.

- QuizService — бизнес-логика (создание квизов, прохождение, подсчёт баллов)
- get_quiz_service — dependency injection

Использует LoggerService для цветного логирования.
"""

from .Service import QuizService, get_quiz_service

__all__ = [
    'QuizService',
    'get_quiz_service',
]