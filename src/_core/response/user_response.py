from typing import Optional, Generic, TypeVar, Any, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import Response
import json
T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """
    Стандартная модель ответа API.
    
    Параметры:
    - success: Успех операции (bool)
    - data: Основные данные ответа (опционально, любого типа)
    - error: Сообщение об ошибке (опционально, строка)
    - meta: Мета-данные (опционально, словарь)
    """
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    meta: Optional[dict] = None

def API_response(
    status_code: int,
    success: bool,
    data: Optional[Any] = None,
    meta: Optional[dict] = None,
    error: Optional[str] = None,
    response: Optional[Response] = None
) -> JSONResponse:
    """
    Формирует стандартизированный JSON-ответ для API.
    Если передан response, то модифицирует его и возвращает его же (с телом).
    Иначе возвращает новый JSONResponse.
    """
    content = ApiResponse(
        success=success,
        data=data,
        error=error,
        meta=meta
    ).dict(exclude_none=True)

    if response is not None:
        response.status_code = status_code
        response.headers["content-type"] = "application/json"
        response.body = json.dumps(content).encode()
        return response
    else:
        return JSONResponse(
            status_code=status_code,
            content=content
        )

def check_isinstance(original: dict, validated: Optional[dict]) -> dict:
    """
    Маленькая функция для проверки типа обькта и его последующего изменения.
    
    - **original**:   Исходный словарь
    - **validated**:  Потенциальный словарь который, будет добавлен в исходный
    
    """
    if isinstance(validated, dict):
        original.update(validated)
    return original
        

def inject_data(*data):
    def ARGV(func):
        def wrapper(*argv, **kwargs):
            result = func(*argv, **kwargs)
            model, description, example, example_append = result
            
            if example_append:
                example = check_isinstance(example, example_append)
            
            response_data = {
                "description": description,
                "model": model,
                "content": {
                    "application/json": {
                        "example": example
                    }
                }
            }
            return response_data
        return wrapper
    return ARGV


class ResponseData:
    """ВНИМАНИЕ К ПАРАМЕТРУ example необходимо только добавлять данные"""
    
    @staticmethod
    def _build_example(default_example: dict, **overrides) -> dict:
        """Базовый метод для создания example с переопределениями"""
        example = default_example.copy()
        for key, value in overrides.items():
            if value is not None:
                example[key] = value
        return example
    
    @staticmethod
    @inject_data()
    def status_200(
        model: BaseModel,
        example_append: Optional[dict] = None,
        description: str = 'Успешный ответ',
        example: Optional[dict] = None
    ):
        if example is None:
            example = {}
            
        return model, description, example, example_append

    @staticmethod
    @inject_data()
    def status_201(
        model: BaseModel,
        example_append: Optional[dict] = None,
        description: str = 'Успешно создан',
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "id": "int",
                    "username": "string",
                    "email": "string@gmail.com"
                }
            )
        return model, description, example, example_append
    
    @staticmethod
    @inject_data()
    def status_202(
        model: BaseModel,
        example_append: Optional[dict] = None,
        expires_in: int = 3600, 
        description: str = 'Успешный вход',
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": expires_in
                },
                expires_in=expires_in
            )
        return model, description, example, example_append
    
    @staticmethod
    def status_204(description: str = 'Запрос выполнен успешно'):
        return {'description': description, 'content': None}
    
    @staticmethod
    @inject_data()
    def status_400(
        model: BaseModel,
        description: str = 'Неверные данные.',
        example_append: Optional[dict] = None,
        detail: Union[dict, str] = "Неверные данные пользователя",
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "detail": detail,
                    "status": 400,
                    "code": "DATA-400"
                },
                detail=detail
            )
        return model, description, example, example_append
    
    @staticmethod
    @inject_data()
    def status_401(
        model: BaseModel,
        description: str = 'Неверные учётные данные.',
        example_append: Optional[dict] = None,
        detail: Union[dict, str] = "Неверный пароль или юзернейм",
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "detail": detail,
                    "status": 401,
                    "code": "AUTH-401"
                },
                detail=detail
            )
        return model, description, example, example_append

    @staticmethod
    @inject_data()
    def status_403(
        model: BaseModel,
        description: str = 'Доступ запрещён.',
        example_append: Optional[dict] = None,
        detail: Union[dict, str] = "У вас нет прав для доступа к этому ресурсу",
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "detail": detail,
                    "status": 403,
                    "code": "FORBIDDEN-403"
                },
                detail=detail
            )
        return model, description, example, example_append

    @staticmethod
    @inject_data()
    def status_404(
        model: BaseModel,
        description: str = 'Ресурс не найден.',
        example_append: Optional[dict] = None,
        detail: Union[dict, str] = "Запрашиваемый ресурс не существует",
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "detail": detail,
                    "status": 404,
                    "code": "NOT-FOUND-404"
                },
                detail=detail
            )
        return model, description, example, example_append
    
    @staticmethod
    @inject_data()
    def status_500(
        model: BaseModel = BaseModel,
        description: str = 'Внутренняя ошибка сервера.',
        example_append: Optional[dict] = None,
        detail: Union[dict, str] = "Internal server error",
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "detail": detail,
                    "status": 500,
                    "code": "SERVER-500"
                },
                detail=detail
            )
        return model, description, example, example_append
    
    @staticmethod
    @inject_data()
    def status_429(
        model: BaseModel = BaseModel,
        description: str = 'Слишком много попыток входа.',
        example_append: Optional[dict] = None,
        detail: Union[dict, str] = "Слишком много попыток. Попробуйте чуть позже",
        example: Optional[dict] = None
    ):
        if example is None:
            example = ResponseData._build_example(
                {
                    "detail": detail,
                    "status": 429,
                    "code": "RATE-LIMIT-429"
                },
                detail=detail
            )
        return model, description, example, example_append