"""Аутентификация и авторизация.

Компоненты:
- register, login, logout — эндпоинты управления сессией
- me — получение профиля текущего пользователя
- AuthTokenMiddleware — извлечение токена из cookie/заголовка
- create_access_token / create_refresh_token — генерация JWT
- get_current_user — dependency для получения пользователя из токена
- token_dispatch — диспетчер для валидации токена
- setup_control, debug_kill_router — утилиты для запуска и отладки
"""

from .jwt import create_access_token, create_refresh_token
from .middleware import AuthTokenMiddleware
from .dependencies import token_dispatch, debug_kill_router, setup_control, get_current_user
from .auth_router import *
from .users_router import profile_router
from fastapi import APIRouter

authentication_router = APIRouter()

authentication_router.include_router(register_router)
authentication_router.include_router(login_router)
authentication_router.include_router(logout_router)
authentication_router.include_router(profile_router)


__all__ = [
    'login_router',
    'register_router', 
    'logout_router',
    'profile_router'
]