"""Pydantic схемы для валидации данных.

Базовые:
- StripStringsModel — автоматически обрезает пробелы во всех строковых полях
- ErrorResponse / ErrorResponseBetter — схемы ошибок

Пользователи:
- UserBase — email, username
- UserCreate — регистрация (+ password)
- UserInDB — пользователь из БД (+ id, status_operation)
- UserLogin — вход (username, password)
- UserLoginResponse / UserCreateResponse — ответы
- CheckUser — проверка существования
- UserDelete — удаление
- CodeResponse — код подтверждения
"""

from .user_schemas import (
    UserBase, 
    UserCreate, 
    UserInDB, 
    UserDelete, 
    CheckUser,
    UserLoginResponse,
    UserLogin,
    UserCreateResponse,
    CodeResponse
    )

from .exceptions import ErrorResponse
from .base_schemas import StripStringsModel

TEXT_FIELD = {
    "min_length": 3,
    "max_length": 100,
    "pattern": r"^[a-zA-Zа-яА-ЯёЁ\s\-]+$"
}
