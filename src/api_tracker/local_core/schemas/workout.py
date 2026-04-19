from pydantic import Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from src._core.schemas import StripStringsModel

TEXT_FIELD = {
    "min_length": 3,
    "max_length": 100,
    "pattern": r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$"
}
_Data_Create = {
    "json_schema_extra": {
        "examples": [
            {
                "name": "Тренировка груди",
                "description": "Интенсивная тренировка на массу",
                "completed_at": "2026-04-03T15:11:24.257Z",
                "exercises": [
                    {
                        "exercise_name": "Жим лежа",
                        "sets": 3,
                        "reps": 10,
                        "weight": 50.5
                    },
                ]
            }
        ]
    }
}

class WorkoutExerciseCreate(StripStringsModel):
    """Схема для создания упражнения в тренировке"""
    exercise_name: str = Field(**TEXT_FIELD)
    sets: int = Field(..., ge=1, le=50, description="Количество подходов")
    reps: int = Field(..., ge=1, le=200, description="Количество повторений")
    weight: Optional[float] = Field(None, ge=0, description="Вес в кг")

class WorkoutCreate(StripStringsModel):
    """Схема для создания тренировки"""
    name: str = Field(**TEXT_FIELD)
    description: Optional[str] = Field(None, max_length=1000)
    completed_at: Optional[datetime] = None
    exercises: List[WorkoutExerciseCreate] = Field(..., min_length=1)
    
    model_config = _Data_Create

class WorkoutFilters(StripStringsModel):
    """Фильтры для получения тренировок"""
    limit: int = Field(100, ge=1, description="Максимальное количество записей")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")

class WorkoutExerciseResponse(StripStringsModel):
    """Ответ с данными упражнения внутри тренировки"""
    id: int
    exercise_id: int
    sets: int
    reps: int
    weight: Optional[float]
    order: int
    
    model_config = ConfigDict(from_attributes=True)

class WorkoutResponse(StripStringsModel):
    """Ответ с данными тренировки"""
    id: int
    name: str = Field(**TEXT_FIELD)
    description: Optional[str]
    user_id: int
    completed_at: datetime
    exercises: List[WorkoutExerciseResponse]
    
    model_config = ConfigDict(from_attributes=True)

class WorkoutUpdate(StripStringsModel):
    """Схема для частичного обновления тренировки"""
    name: Optional[str] = Field(None, **TEXT_FIELD)
    description: Optional[str] = Field(None, max_length=1000)
    completed_at: Optional[datetime] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Новый жим лежа",
                    "description": "Попки",
                    "completed_at": "2026-04-04T10:00:00"
                }
            ]
        }
    }