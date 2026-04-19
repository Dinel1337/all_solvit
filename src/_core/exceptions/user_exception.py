from .app_exception import AppException
from ..enum import ErrorUser, ErrorEmail
from fastapi import status
from .main_error import BadParametrError, NotFoundError
from typing import Optional, Any

suggestions_email = {
    "TYPE_ERROR": "Email должен быть строкой, например 'user@example.com'",
    "VALIDATION_ERROR": "Используйте формат user@example.com",
    "UNKNOWN_ERROR": "Попробуйте другой email или повторите позже"
}

suggestions_password = {
    "TYPE_ERROR": "Пароль должен быть строкой",
    "VALIDATION_ERROR": "Пароль должен содержать минимум 6 символов, включая буквы",
    "UNKNOWN_ERROR": "Попробуйте другой пароль или повторите позже",
    "TOO_SHORT": "Пароль должен содержать минимум 6 символов",
    "TOO_LONG": "Пароль должен содержать максимум 32 символа",
}

class UserNotFound(NotFoundError):
    """Пользователь не найден"""
    
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
            resource="User",
            search_param=search_param,
            search_field=search_field,
            message=message or f"Пользователь по полю '{search_field}' со значением '{search_param}' не найден",
            error_code="USER_NOT_FOUND",
            details=details
        )

class UserErrorCreateException(AppException):
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code = ErrorUser.USER_NOT_CREATED.value,
            message = f"User {username} not created",
            details = {
                'username': username,
                'suggestion': 'Try another user class'
            }
        )                     

class UserEmailExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code=ErrorUser.USER_EMAIL_EXIST.value,
            message="Email уже существует",
            details={
                'email': email,
                'suggestion': 'Try another email address'
            }
        )

class EmailValidationError(AppException):
    """Ошибка валидации email с детализацией типа ошибки"""
    def __init__(self ,email: str, reason: str, more: Optional[str], error_type: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code=ErrorEmail.INVALID_EMAIL.value,
            message="Некорректный email адрес",
            details={
                "email": email,
                "reason": reason,
                "error_type": error_type,
                "suggestion": self._get_suggestion(error_type, suggestions_email, "Используйте корректный email адресс"),
                'more' : more
            }
        )
    

class PasswordValidationError(AppException):
    """Ошибки валидации password с детализацией типа ошибки"""

    def __init__(self,
                reason: str,
                more: Optional[str] = None,
                error_type: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            error_code=ErrorEmail.INVALID_EMAIL.value,
            message="Некорректный пароль",
            details={
                "reason": reason,
                "error_type": error_type,
                "suggestion": self._get_suggestion(error_type, suggestions_password, "Используйте другой пароль"),
                'more' : more
            }
        )
        

class UserBadParametrError(BadParametrError):
    def __init__(
        self, parameter: str | None = None):
        super().__init__(
            error_code = ErrorUser.USER_BAD_PARAMETR.value,
            message = "Bad request user parametr, other data",
            parametr = parameter
            )