"""Кастомные исключения для API Tracker.

Используются с RaiseControl для автоматической генерации 404.

Упражнения:
- ExerciseNotFoundError — упражнение не найдено
- CategoryNotFoundError — категория не найдена
- MuscleGroupNotFoundError — группа мышц не найдена

Тренировки:
- WorkoutNotFoundError — тренировка не найдена
- WorkoutExerciseNotFoundError — упражнение в тренировке не найдено
"""

from .workoute import (
    ExerciseNotFoundError,
    CategoryNotFoundError,
    MuscleGroupNotFoundError,
    WorkoutNotFoundError,
    WorkoutExerciseNotFoundError,
)

__all__ = [
    'ExerciseNotFoundError',
    'CategoryNotFoundError',
    'MuscleGroupNotFoundError',
    'WorkoutNotFoundError',
    'WorkoutExerciseNotFoundError',
]