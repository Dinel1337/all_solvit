from src._core.exceptions import AppException, NotFoundError
from fastapi import status
from typing import Any, Optional

class AttemptNotFoundError(NotFoundError):
    def __init__(
        self,
        search_param: Any,
        search_field: str = "id",
        message: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            resource="Attempt",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Попытка по полю '{search_field}' со значением '{search_param}' не найдена",
            error_code="ATTEMPT_NOT_FOUND",
            **kwargs
        )

class AttemptAlreadyFinishedError(AppException):
    def __init__(self, attempt_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="ATTEMPT_ALREADY_FINISHED",
            message=f"Попытка {attempt_id} уже завершена",
            details={"attempt_id": attempt_id}
        )

class QuizNotPublishedError(AppException):
    def __init__(self, quiz_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="QUIZ_NOT_PUBLISHED",
            message=f"Викторина {quiz_id} не опубликована",
            details={"quiz_id": quiz_id}
        )

class InvalidAnswerError(AppException):
    def __init__(self, question_id: int, option_id: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_ANSWER",
            message=f"Вариант ответа {option_id} не принадлежит вопросу {question_id}",
            details={"question_id": question_id, "option_id": option_id}
        )