"""Аутентификация и управление пользователями.

Покрывает:
- POST /auth/register — регистрация, валидация email/username/password
- POST /auth/login — вход, выдача JWT в cookie
- POST /auth/logout — выход, инвалидация токена

Токен передаётся:
- В cookie: access_token (HttpOnly, Secure)
- В заголовке: Authorization: Bearer <token>
"""

from .login import router as login_router
from .register import router as register_router
from .logout import router as logout_router

__all__ = [
    'login_router',
    'register_router', 
    'logout_router'
]