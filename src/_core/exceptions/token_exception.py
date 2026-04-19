from .app_exception import AppException
from fastapi import status
from typing import Optional

class TokenUnauthorized(AppException):
    def __init__(
            self, 
            username: str,
            meta: Optional[dict] | Optional[str] = None,
            message : Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message if message else "Невалидный токен, перезагрузите сайт",
            details={
                'username': username,
                'meta': meta,
            }
        ) # можно добавить error_type в будующем зависимый от метода _get_suggestion в AppException

