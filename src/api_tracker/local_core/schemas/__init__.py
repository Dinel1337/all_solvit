"""Pydantic схемы для API Tracker.

Упражнения:
- CreateCategory / CreateMuscle / CreateExercise — создание
- CategoryResponse / MuscleResponse / ExerciseResponse — ответы
- ExerciseQuery — поиск по name/description/category/muscle_group

Тренировки:
- WorkoutCreate / WorkoutUpdate — создание/обновление
- WorkoutResponse / WorkoutExerciseResponse — ответы
- WorkoutFilters — пагинация (limit, offset)

Сводка:
- DateRangeQuery — период (from_date, to_date)
- SummaryResponse — статистика за период
- DailyProgressResponse — дневная динамика
"""

from .Exercise import (
    ExerciseInDatabase,
    CreateExercise,
    CreateCategory,
    CreateMuscle,
    CategoryInDatabase,
    MuscleInDatabase,
    MuscleResponse,
    CategoryResponse,
    ExerciseResponse,
    ExerciseQuery,
)
from .workout import (
    WorkoutCreate,
    WorkoutExerciseCreate,
    WorkoutResponse,
    WorkoutExerciseResponse,
    WorkoutFilters,
    WorkoutUpdate,
)
from .summary import SummaryResponse, DateRangeQuery, DailyProgressResponse

__all__ = [
    "ExerciseInDatabase",
    "CreateExercise",
    "CreateCategory",
    "CreateMuscle",
    "CategoryInDatabase",
    "MuscleInDatabase",
    "MuscleResponse",
    "CategoryResponse",
    "ExerciseResponse",
    "ExerciseQuery",
    "WorkoutCreate",
    "WorkoutExerciseCreate",
    "WorkoutResponse",
    "WorkoutExerciseResponse",
    "WorkoutFilters",
    "WorkoutUpdate",
    "SummaryResponse",
    "DateRangeQuery",
    "DailyProgressResponse",
]