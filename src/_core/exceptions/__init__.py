"""Кастомные исключения приложения.

Базовые:
- AppException — корневое исключение, наследуется от HTTPException
- BadParametrError — 400, неверные параметры
- NotFoundError — 404, ресурс не найден
- AccessDeniedError — 403, недостаточно прав
- NotOwnerError — 403, пользователь не владелец ресурса

Токены:
- TokenUnauthorized — 401, невалидный или отсутствующий токен

Пользователи:
- UserNotFound — 404, пользователь не найден
- UserEmailExistsException — 409, email уже существует
- UserErrorCreateException — 400, ошибка создания
- UserBadParametrError — 400, неверные параметры
- EmailValidationError — 422, невалидный email
- PasswordValidationError — 422, невалидный пароль
"""

from .user_exception import (
                         UserErrorCreateException,
                         UserEmailExistsException,
                         UserBadParametrError,
                         EmailValidationError,
                         PasswordValidationError,
                         UserNotFound
                         )

from .main_error import(
    BadParametrError, NotFoundError, AccessDeniedError, NotOwnerError
)

from .app_exception import AppException
from .token_exception import TokenUnauthorized


__all__ = [
    name for name, obj in globals().items() 
    if not name.startswith('_') 
    and not isinstance(obj, type(__import__('sys')))
]