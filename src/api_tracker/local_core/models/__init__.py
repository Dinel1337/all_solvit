"""SQLAlchemy модели для API Tracker.

Упражнения:
- Category — категория упражнения
- MuscleGroup — группа мышц
- Exercise — упражнение (связь с category и muscle_group)

Тренировки:
- Workout — тренировка пользователя
- WorkoutExercise — связь тренировки с упражнениями (сеты, повторы, вес, порядок)
"""

from .exercises_model import Exercise, Category, MuscleGroup
from .workoute_model import Workout, WorkoutExercise

__all__ = [
    'Exercise',
    'Category',
    'MuscleGroup',
    'Workout',
    'WorkoutExercise',
]