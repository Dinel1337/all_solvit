"""Профиль текущего пользователя.

Покрывает:
- GET /users/me — получение профиля авторизованного пользователя

Требования:
- Валидный access_token в cookie или заголовке Authorization: Bearer
"""

from .me import router as profile_router