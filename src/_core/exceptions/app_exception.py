from fastapi import HTTPException
from enum import Enum

class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        error_code: Enum | None = None,
        message: str | None = None,
        details: dict | None = None
    ):

        super().__init__(
            status_code=status_code,
            detail={
                'error_code': error_code,
                'message': message,
                'details': details or {}
            }
        )
    def _get_suggestion(self,
                        error_type: str, 
                        suggestions: dict,
                        response_message: str) -> str:
        """Возвращает подсказку в зависимости от типа ошибки"""
    
        suggestions = suggestions

        return suggestions.get(error_type, response_message)   
        