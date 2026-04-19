"""API роутеры для API Tracker.

Объединяет все эндпоинты:
- exercises — категории, группы мышц, упражнения
- workouts — создание, получение, обновление, удаление тренировок
- reports — сводка и динамика прогресса

Все эндпоинты требуют авторизации через get_current_user (JWT в cookie/заголовке).
"""
from fastapi import APIRouter

from .exercises import *
from .workouts import *
from .reports import *

router = APIRouter()

router.include_router(exercises_router)
router.include_router(category_router)
router.include_router(muscle_router)
router.include_router(router_workout_public)
router.include_router(router_workout_private)
router.include_router(summary_router)
