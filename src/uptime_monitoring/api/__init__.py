"""API роутеры для Quiz Platform.

Объединяет все эндпоинты:
- quizzes — создание, публикация, получение квизов
- attempts — прохождение, сохранение ответов, результаты

Все эндпоинты используют get_current_user для авторизации (JWT в cookie/заголовке).
"""

from fastapi import APIRouter
from .domain import router as add_domain_router

router = APIRouter()

router.include_router(add_domain_router)