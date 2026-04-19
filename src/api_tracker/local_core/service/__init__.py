"""Сервисный слой для API Tracker.

Предоставляет:
- ExerciseService — бизнес-логика упражнений, категорий, групп мышц
- Управление тренировками (создание, обновление, удаление)
- Статистика и сводки (недельная, за период)
- Кэширование ID категорий и групп мышц

Использует:
- ExerciseRepository, WorkoutRepository, WorkoutExerciseRepository
- RaiseControl для обработки 404
- LoggerService для цветного логгирования
"""

from .Service import ExerciseService, get_exercise_service

__all__ = [
    'ExerciseService',
    'get_exercise_service',
]