from pydantic import ConfigDict, Field
from typing import List,Optional, Literal
from src._core.schemas import StripStringsModel

_example_quiz_json = {
    "name": "Python Basics Quiz",
    "description": "Тест по основам Python",
    "status": "published",
    "questions": [
        {
            "text": "Что выведет print(2 + 2)?",
            "points": 2,
            "order": 0,
            "options": [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True},
                {"text": "5", "is_correct": False}
            ]
        },
        {
            "text": "Какой тип данных у 'hello'?",
            "points": 1,
            "order": 1,
            "options": [
                {"text": "int", "is_correct": False},
                {"text": "str", "is_correct": True},
                {"text": "list", "is_correct": False}
            ]
        }
    ]
}


class CreateBaseModel(StripStringsModel):
    """Для записи в БД (Request)"""
    model_config = ConfigDict(from_attributes=True)

class AnswerOptionCreate(CreateBaseModel):
    text: str
    is_correct: bool = False


class QuestionCreate(CreateBaseModel):
    text: str
    points: int = Field(ge = 1, default=1)
    order: int = Field(ge = 0, default=0)
    options: List[AnswerOptionCreate] = Field(..., min_length=2)


class QuizCreate(CreateBaseModel):
    name: str
    description: Optional[str] = None
    status: Literal['draft', 'published'] = "draft"
    questions: List[QuestionCreate]
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": _example_quiz_json
        }
    )

class AttemptCreate(CreateBaseModel):
    quiz_id: int = Field(ge=1)
    user_id: Optional[int] = Field(None, ge=1)
    anonymous_token: Optional[str] = None


class UserAnswerCreate(CreateBaseModel):
    attempt_id: int = Field(ge=1)
    question_id: int = Field(ge=1)
    selected_option_id: int = Field(ge=1)


class AnswerItem(StripStringsModel):
    question_id: int = Field(ge=1)
    selected_option_id: int = Field(ge=1)

class AnswersBulkCreate(StripStringsModel):
    answers: List[AnswerItem]
    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                  "answers": [
                    {
                      "question_id": 1,
                      "selected_option_id": 2
                    },
                    {
                      "question_id": 2,
                      "selected_option_id": 3
                    },
                  ]
                }
            }
        )