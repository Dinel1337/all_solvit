"""Эндпоинты прохождения квизов.

Покрывает:
- POST /quizzes/{quiz_id}/attempts — начать прохождение
- PUT /attempts/{attempt_id}/answers — сохранение ответов
- POST /attempts/{attempt_id}/finish — завершить попытку
- GET /attempts/{attempt_id}/result — получить результат

Поддерживает авторизованных и анонимных пользователей (anonymous_token).
"""

from .crud import router as attempt_router

__all__ = [
    'attempt_router',
]