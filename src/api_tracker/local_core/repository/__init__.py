"""Репозитории для API Tracker.

Используют RaiseControl для автоматической генерации 404.

Упражнения:
- ExerciseRepository — CRUD упражнений, поиск по name/category/muscle_group

Тренировки:
- WorkoutRepository — CRUD тренировок, фильтрация по user_id/датам, статистика
- WorkoutExerciseRepository — управление упражнениями внутри тренировки
"""

from .ExerciseRepository import ExerciseRepository
from .workouts_repository import WorkoutRepository, WorkoutExerciseRepository

__all__ = [
    'ExerciseRepository',
    'WorkoutRepository',
    'WorkoutExerciseRepository',
]