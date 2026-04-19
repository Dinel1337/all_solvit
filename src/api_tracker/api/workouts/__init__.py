"""Эндпоинты управления тренировками.

Покрывает:
- POST /workouts/ — создание тренировки с упражнениями
- GET /workouts/ — список тренировок пользователя (фильтр limit)
- GET /workouts/{workout_id} — получение тренировки по ID
- PATCH /workouts/{workout_id} — частичное обновление тренировки
- DELETE /workouts/{workout_id} — удаление тренировки

Все эндпоинты требуют авторизации (JWT в cookie или заголовке).
Доступ к тренировке — только владельцу (проверка user_id).
"""

from .get_create import router as router_workout_public
from .update_delete import router as router_workout_private

__all__ = [
    'router_workout_public',
    'router_workout_private',
]