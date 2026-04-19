"""Эндпоинты отчетов и статистики.

Покрывает:
- GET /reports/summary — сводка по тренировкам за период (workouts_done, total_sets, total_reps, total_volume)
- GET /reports/progress — дневная динамика прогресса (date, volume, workouts)

Все эндпоинты требуют авторизации (JWT в cookie или заголовке).
"""

from .summary import router as summary_router

__all__ = [
    'summary_router',
]