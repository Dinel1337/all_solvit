"""Репозитории для работы с БД.

Предоставляет:
- BaseRepository — generic CRUD операции (find_one_by, create, update_by_id, delete_by_id)
- UserRepository — репозиторий пользователей и токенов

Утилиты:
- RaiseControl — декоратор для автоматической генерации 404 при None
"""
from .user_repository import UserRepository

__all__ = [
    name for name, obj in globals().items() 
    if not name.startswith('_') 
    and isinstance(obj, type)
]