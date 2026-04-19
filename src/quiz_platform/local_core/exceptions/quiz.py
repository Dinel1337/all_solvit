from typing import Optional, Any
from src._core.exceptions import NotFoundError

class QuizNotFoundError(NotFoundError):
    """Викторина не найдена"""
    
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
            resource="Quiz",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Викторина по полю '{search_field}' со значением '{search_param}' не найдена",
            error_code="QUIZ_NOT_FOUND",
            details=details
        )


class QuestionNotFoundError(NotFoundError):
    """Вопрос не найден"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "text"
        
        super().__init__(
            resource="Question",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Вопрос по полю '{search_field}' со значением '{search_param}' не найден",
            error_code="QUESTION_NOT_FOUND",
            details=details
        )


class AnswerOptionNotFoundError(NotFoundError):
    """Вариант ответа не найден"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "text"
        
        super().__init__(
            resource="AnswerOption",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Вариант ответа по полю '{search_field}' со значением '{search_param}' не найден",
            error_code="ANSWER_OPTION_NOT_FOUND",
            details=details
        )


class AttemptNotFoundError(NotFoundError):
    """Попытка прохождения не найдена"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "anonymous_token"
        
        super().__init__(
            resource="Attempt",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Попытка по полю '{search_field}' со значением '{search_param}' не найдена",
            error_code="ATTEMPT_NOT_FOUND",
            details=details
        )


class UserAnswerNotFoundError(NotFoundError):
    """Ответ пользователя не найден"""
    
    def __init__(
        self,
        search_param: Any,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if search_field is None:
            search_field = "id" if isinstance(search_param, int) else "attempt_id"
        
        super().__init__(
            resource="UserAnswer",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Ответ пользователя по полю '{search_field}' со значением '{search_param}' не найден",
            error_code="USER_ANSWER_NOT_FOUND",
            details=details
        )