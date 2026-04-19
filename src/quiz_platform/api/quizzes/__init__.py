"""Эндпоинты управления квизами.

Покрывает:
- POST /quizzes/ — создание квиза с вопросами и опциями
- GET /quizzes/ — список опубликованных квизов (пагинация, поиск)
- GET /quizzes/{quiz_id} — получение квиза по ID
- PUT /quizzes/{quiz_id}/publish — публикация/снятие с публикации

Все эндпоинты требуют авторизации.
"""

from .crud import router as crud_router
from .give import router as give_quiz_router
from .publish import router as publish_router

__all__ = [
    'crud_router',
    'give_quiz_router',
    'publish_router',
]