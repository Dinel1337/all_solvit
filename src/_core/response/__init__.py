"""Формирование стандартизированных ответов API.

Компоненты:
- API_response — единая функция для JSON-ответов (success/data/meta)
- construct_meta — конструктор мета-данных (timestamp, reason, other)
- ApiResponse — Pydantic модель ответа (success, data, error, meta)
- ResponseData — фабрика Swagger-ответов для эндпоинтов (200, 201, 202, 204, 400, 401, 403, 404, 429, 500)
"""

from .meta import construct_meta
from .user_response import ApiResponse, API_response, ResponseData


__all__ = [
    name for name, obj in globals().items() 
    if not name.startswith('_') 
    and isinstance(obj, type)
]