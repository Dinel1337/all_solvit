from email_validator import validate_email, EmailNotValidError
from ..exceptions import EmailValidationError, PasswordValidationError
from typing import Any

def validate_email_address(email: Any) -> str:
    """
    Универсальный валидатор email, который обрабатывает:
    - EmailNotValidError (из email-validator)
    - TypeError (если передали не строку)
    - ValueError (некорректный формат)
    - Любые другие ошибки
    """
    if not isinstance(email, str):
        raise EmailValidationError(
            email=email,
            reason="type is not valid, use 'email' format",
            error_type="TYPE_ERROR"
        )
    try:
        validate = validate_email(email)
        return validate.normalized
    
    except EmailNotValidError as e:
        raise EmailValidationError(
            email=email,
            reason="Введите корректный email адрес",
            error_type="VALIDATION_ERROR",
            more=str(e)
        )
    
    except Exception as e:
        raise EmailValidationError(
            email=email,
            reason="Неожиданные ошибки",
            error_type="VALIDATION_ERROR"
        )

def password_length_check(password: Any):
    """
    Проверяет пароль на длину и корректность
    """
    if not isinstance(password, str):
        raise PasswordValidationError(
            reason="Пароль должен быть строкой",
            error_type="VALIDATION_ERROR"
        )

    if len(password) < 6:
        raise PasswordValidationError(
            reason="Минимальная длина 6 символов",
            error_type="TOO_SHORT"
        )
    
    if len(password) > 32:
        raise PasswordValidationError(
            reason="Минимальная длина 6 символов",
            error_type="TOO_LONG"
        )
    
    return password