from fastapi import status
from typing import Optional, Any
from .app_exception import AppException

class BadParametrError(AppException):
    """Возвращает ошибку при неверных параметрах"""
    def __init__(
        self,
        parametr: Optional[str] = None,
        message: str = "Bad request parametr",
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        base_details = {'parameter': parametr}
        if details:
            base_details.update(details)
            
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            message=message,
            details=base_details
        )

class NotFoundError(AppException):
    """Возвращает ошибку 404 когда ресурс не найден"""
    
    def __init__(
        self,
        resource: Optional[str] = None,
        search_param: Optional[Any] = None,
        search_field: Optional[str] = None,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        if message is None:
            if resource and search_param is not None:
                if search_field:
                    message = f"{resource} с {search_field} '{search_param}' не найден(а)"
                else:
                    message = f"{resource} с параметром '{search_param}' не найден(а)"
            elif resource:
                message = f"{resource} не найден(а)"
            else:
                message = "Ресурс не найден"
        
        base_details = {}
        if resource:
            base_details['resource'] = resource
        if search_param is not None:
            base_details['search_param'] = search_param
        if search_field:
            base_details['search_field'] = search_field
        if details:
            base_details.update(details)
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code or "RESOURCE_NOT_FOUND",
            message=message,
            details=base_details
        )

class AccessDeniedError(AppException):
    """Ошибка доступа - недостаточно прав"""
    
    def __init__(
        self,
        message: str = "Доступ запрещён",
        error_code: str = "ACCESS_DENIED",
        details: Optional[dict] = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            message=message,
            details=details
        )


class NotOwnerError(AccessDeniedError):
    """Ошибка - пользователь не является владельцем ресурса"""
    
    def __init__(
        self,
        resource: str = "ресурс",
        message: Optional[str] = None,
        details: Optional[dict] = None
    ) -> None:
        super().__init__(
            message=message or f"Вы не являетесь владельцем {resource}",
            error_code="NOT_OWNER",
            details=details
        )