from pydantic import ConfigDict, Field
from datetime import datetime
from typing import Optional
from src._core.schemas import StripStringsModel

NAME_MIN_LENGTH = 3
NAME_MAX_LENGTH = 50
NAME_PATTERN = r"^[a-zA-Zа-яА-Я]+$"
TEXT_FIELD = {
    "min_length": 3,
    "max_length": 100,
    "pattern": r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$"
}
_Category = {
    "json_schema_extra": {
        "examples": [
            {
                "name": "Силовая",
                "description": "Имеет весик"
            }
        ]
    }
}

_Muscle = {
    "json_schema_extra": {
        "examples": [
            {
                "name": "Грудь",
                "description": "Сисички"
            }
        ]
    }
}

_Exercise = {
    "json_schema_extra": {
        "examples": [
            {
                "name": "Жим лежа",
                "description": "Сгибание бла бла бла бла",
                "category": "Силовая",
                "muscle_group": "Грудь"
            }
        ]
    }
}

class BaseWithId(StripStringsModel):
    """Примесь, добавляющая id для объектов из БД"""
    id: int
    model_config = ConfigDict(from_attributes=True)

class CreateExercise(StripStringsModel):
    name: str = Field(**TEXT_FIELD)
    description: str | None = None
    category: str | None = None    
    muscle_group: str | None = None
    model_config = ConfigDict(**_Exercise)

class CreateMuscle(StripStringsModel):
    name: str = Field(
        min_length=NAME_MIN_LENGTH,
        max_length=NAME_MAX_LENGTH,
        pattern=NAME_PATTERN
    )
    description: str | None = None
    model_config = ConfigDict(**_Muscle)

class CreateCategory(CreateMuscle):
    model_config = ConfigDict(**_Category)

class ExerciseResponse(BaseWithId):
    """Схема для ответа с упражнением"""
    name: str = None
    description: str | None = None
    category: str | None = None    
    muscle_group: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class MuscleResponse(BaseWithId):
    """Схема для ответа с группой мышц"""
    name: str
    description: str | None = None

class CategoryResponse(BaseWithId):
    """Схема для ответа с категорией"""
    name: str
    description: str | None = None

class ExerciseQuery(StripStringsModel):
    name: Optional[str] = Field(None, **TEXT_FIELD)
    description: Optional[str] = Field(None, **TEXT_FIELD)
    category: Optional[str] = Field(None, **TEXT_FIELD)
    muscle_group: Optional[str] = Field(None, **TEXT_FIELD)

ExerciseInDatabase = ExerciseResponse
MuscleInDatabase = MuscleResponse
CategoryInDatabase = CategoryResponse