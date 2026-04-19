"""API роутеры для Quiz Platform.

Объединяет все эндпоинты:
- quizzes — создание, публикация, получение квизов
- attempts — прохождение, сохранение ответов, результаты

Все эндпоинты используют get_current_user для авторизации (JWT в cookie/заголовке).
"""

from fastapi import APIRouter
from .quizzes import crud_router, give_quiz_router, publish_router
from .attemps import attempt_router

router = APIRouter()

router.include_router(crud_router)
router.include_router(give_quiz_router)
router.include_router(publish_router)
router.include_router(attempt_router)
