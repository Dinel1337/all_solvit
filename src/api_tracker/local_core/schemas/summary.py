from src._core.schemas import StripStringsModel
from pydantic import Field, ConfigDict
from datetime import date
from typing import List

class DateRangeQuery(StripStringsModel):
    from_date: date
    to_date: date

class SummaryResponse(DateRangeQuery):
    """Сводка по тренировкам за период"""
    workouts_done: int = 0
    total_sets: int = 0
    total_reps: int = 0
    total_volume: float = 0.0
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "from_date": "2026-04-01",
                    "to_date": "2026-04-07",
                    "workouts_done": 5,
                    "total_sets": 45,
                    "total_reps": 380,
                    "total_volume": 4250.5
                }
            ]
        }
    )

class DailyProgressResponse(StripStringsModel):
    """Дневная динамика прогресса"""
    date: date
    volume: float