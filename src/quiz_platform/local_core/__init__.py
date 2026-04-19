"""Локальное ядро Quiz Platform.

Взаимодействует с _core:
- DatabaseManager — схема quiz_platform
- RaiseControl — обработка 404 (QuizNotFoundError, AttemptNotFoundError)
- BaseRepository — generic CRUD
- LoggerService — цветное логирование
- StripStringsModel — авто-очистка строк

Содержит:
- exceptions — кастомные ошибки (QuizNotFoundError, AttemptNotFoundError и др.)
- models — SQLAlchemy модели (Quiz, Question, Option, Attempt, UserAnswer)
- repository — репозитории с RaiseControl
- schemas — Pydantic схемы (CreateQuiz, QuizResponse, SubmitAttempt)
- service — бизнес-логика (QuizService)
"""

from .exceptions import *
from .models import *
from .repository import *
from .schemas import *
from .service import *

__all__ = []