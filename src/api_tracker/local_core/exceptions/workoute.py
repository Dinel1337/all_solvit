from fastapi import status
from typing import Optional, Type, Any
from src._core.exceptions import NotFoundError

class ExerciseNotFoundError(NotFoundError):
    """Упражнение не найдено"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "name"
        
        super().__init__(
            resource="Exercise",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Упражнение по полю '{search_field}' со значением '{search_param}' не найдено",
            error_code="EXERCISE_NOT_FOUND",
            details=details
        )

class CategoryNotFoundError(NotFoundError):
    """Категория не найдена"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "name"
        
        super().__init__(
            resource="Category",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Категория по полю '{search_field}' со значением '{search_param}' не найдена",
            error_code="CATEGORY_NOT_FOUND",
            details=details
        )


class MuscleGroupNotFoundError(NotFoundError):
    """Группа мышц не найдена"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "name"
        
        super().__init__(
            resource="MuscleGroup",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Группа мышц по полю '{search_field}' со значением '{search_param}' не найдена",
            error_code="MUSCLE_GROUP_NOT_FOUND",
            details=details
        )


class WorkoutNotFoundError(NotFoundError):
    """Тренировка не найдена"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "name"
        
        super().__init__(
            resource="Workout",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Тренировка по полю '{search_field}' со значением '{search_param}' не найдена",
            error_code="WORKOUT_NOT_FOUND",
            details=details
        )

class WorkoutExerciseNotFoundError(NotFoundError):
    """Упражнение в тренировке не найдено"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "workout_id"
        
        super().__init__(
            resource="WorkoutExercise",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Упражнение в тренировке по полю '{search_field}' со значением '{search_param}' не найдено",
            error_code="WORKOUT_EXERCISE_NOT_FOUND",
            details=details
        )