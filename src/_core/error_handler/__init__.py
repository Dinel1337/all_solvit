"""Глобальная обработка ошибок.

Обработчики:
- AppException — кастомные исключения приложения
- NotFoundError — 404 ресурс не найден
- Exception — непредвиденные ошибки (500)

В режиме DEBUG в ответе передаются детали исключения.
"""
from .setup import setup_exception_handlers

__all__ = [
    name for name, obj in globals().items() 
    if not name.startswith('_') 
    and not isinstance(obj, type(__import__('sys')))  # не модуль
]