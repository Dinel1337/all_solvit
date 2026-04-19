"""Эндпоинты управления упражнениями.

Покрывает:
- POST /categories/ — создание категории
- GET /categories/ — список категорий (фильтр по name, description)
- POST /muscles/ — создание группы мышц
- GET /muscles/ — список групп мышц (фильтр по name, description)
- POST /exercises/ — создание упражнения
- GET /exercises/ — список упражнений (фильтр по name, description, category, muscle_group)
- GET /exercises/{exercise_id} — получение упражнения по ID

Все эндпоинты требуют авторизации (JWT в cookie или заголовке).
"""

from .category import router as category_router
from .exercises import router as exercises_router
from .muscle import router as muscle_router

__all__ = [
    'category_router',
    'exercises_router',
    'muscle_router',
]