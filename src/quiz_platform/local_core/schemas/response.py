from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

class ORMBaseModel(BaseModel):
    """Для чтения из БД (Response)"""
    class Config:
        from_attributes = True
        
class AnswerOptionResponse(ORMBaseModel):
    id: int = Field(ge=1)
    text: str
    is_correct: bool

class QuestionResponse(ORMBaseModel):
    id: int = Field(ge=1)
    text: str
    points: int
    order: int
    options: List[AnswerOptionResponse]

class QuizResponse(ORMBaseModel):
    id: int = Field(ge=1)
    name: str
    description: Optional[str]
    status: str
    author_id: int
    questions: List[QuestionResponse]

class AttemptResponse(ORMBaseModel):
    id: int = Field(ge=1)
    quiz_id: int
    user_id: Optional[int]
    anonymous_token: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime]
    total_score: int

class UserAnswerResponse(ORMBaseModel):
    id: int = Field(ge=1)
    attempt_id: int
    question_id: int
    selected_option_id: int
    
    
class QuizFilters(BaseModel):
    """Фильтры для списка викторин"""
    search: Optional[str| int] = Field(None, description="Фильтр по названию")
    limit: int = Field(100, ge=1, le=500, description="Количество записей")
    offset: int = Field(0, ge=0, description="Отступ для пагинации")

class Publish(BaseModel):
    publish: Literal['draft', 'published'] = Field(
        default='draft',
        description="Статус: draft - черновик, published - опубликовано"
    )