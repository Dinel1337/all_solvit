from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from typing import Optional, List
from ...config import EXERCISES_PREFIX, EXERCISES_TAGS

from sqlalchemy.exc import IntegrityError
from src._core.exceptions import NotFoundError
from src._core.schemas import UserBase, ErrorResponse
from src.api_tracker.local_core.schemas import ExerciseInDatabase, CreateExercise, ExerciseQuery
from src.api_tracker.local_core.service import ExerciseService, get_exercise_service
from src._core.response import API_response, construct_meta, ResponseData
from ..dependencies import get_current_user

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=EXERCISES_PREFIX,
    tags=EXERCISES_TAGS,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(List[ExerciseInDatabase]),
        status.HTTP_201_CREATED: ResponseData.status_201(ExerciseInDatabase),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

# ==================== POST ====================
@router.post(
    '/',
    summary="Создать новое упражнение",
    description="""
    Создание нового упражнения в базе данных.
    
    **Процесс:**
    1. Валидация входных данных
    2. Проверка на существование упражнения
    3. Создание записи в БД
    4. Возврат созданного упражнения с ID
    
    **Требования:**
    - Авторизация пользователя
    - Уникальное имя упражнения
    """,
    response_description="Созданное упражнение",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(
            ExerciseInDatabase,
            example={
                "id": 1,
                "name": "Жим лежа",
                "description": "Базовое упражнение на грудь",
                "category": "силовые",
                "muscle_group": "грудь"
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Exercise already exists",
                "status": 400,
                "code": "EX-400"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def add_exercises(
    body: CreateExercise,
    response: Response,
    service: ExerciseService = Depends(get_exercise_service),
    user: UserBase = Depends(get_current_user)
) -> JSONResponse:
    
    try:
        result = await service.create_exercise(body)
        
        if result:
            return API_response(
                status_code=status.HTTP_201_CREATED,
                success=True,
                data=ExerciseInDatabase.model_validate(result),
                meta=construct_meta(
                    reason="Упражнение создано успешно",
                    other={"exercise_id": result.id if hasattr(result, 'id') else None}
                ),
                response=response
            )
        else:
            return API_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Неудалось создать\n\n Смотри доступные данные",
                    other={"error": "Unknown error"}
                ),
                response=response
            )
    
    except (ValueError, IntegrityError) as e:
        logger.warning(f"Ошибка создания упражнения: {e}")
        return API_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            data=None,
            meta=construct_meta(
                reason="Неправильные данные или упражнение уже существует",
                other={"error": str(e)}
            ),
            response=response
        )
    except (NotFoundError, Exception):
        raise

# ==================== GET ====================
@router.get(
    '/',
    summary="Получить список упражнений",
    description="""
    Получение списка упражнений с возможностью фильтрации.
    
    **Параметры фильтрации:**
    - `name` - поиск по названию (частичное совпадение)
    - `description` - поиск по описанию (частичное совпадение)
    - `category` - фильтр по категории
    - `muscle_group` - фильтр по группе мышц
    
    **Примеры:**
    - `GET /exercises/` - все упражнения
    - `GET /exercises/?category=силовые` - только силовые
    - `GET /exercises/?name=жим` - поиск по имени
    """,
    response_description="Список упражнений",
    status_code=status.HTTP_200_OK,
    responses={
    status.HTTP_200_OK: {
        "description": "Успешный запрос — упражнения найдены",
        "model": list[ExerciseInDatabase],
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": [
                        {
                            "id": 1,
                            "name": "жим лежа",
                            "description": "сгибание бла бла бла бла",
                            "category": "силовая",
                            "muscle_group": "грудь"
                        }
                    ],
                    "meta": {
                        "timestamp": "2026-04-14T01:17:51.998526+00:00",
                        "reason": "Успешно найдены упражнения",
                        "other": {
                            "total_count": 1,
                            "filters": {
                                "name": None,
                                "description": None,
                                "category": None,
                                "muscle_group": None
                            }
                        }
                    }
                }
            }
        }
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "Упражнения по заданным фильтрам не найдены",
        "model": list,
        "content": {
            "application/json": {
                "example": {
                    "success": True,
                    "data": [],
                    "meta": {
                        "timestamp": "2026-04-14T01:17:51.998526+00:00",
                        "reason": "Ничего не найдено",
                        "other": {
                            "total_count": 0,
                            "filters": {
                                "name": "несуществующее",
                                "description": None,
                                "category": None,
                                "muscle_group": None
                            }
                        }
                    }
                }
            }
        }
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "Ошибка валидации параметров запроса",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "detail": "Ошибка фильтрации: некорректные параметры",
                    "status": 400,
                    "code": "EX-400"
                }
            }
        }
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": "Пользователь не авторизован",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "detail": "Not authenticated",
                    "status": 401,
                    "code": "AUTH-401"
                }
            }
        }
    },
    status.HTTP_422_UNPROCESSABLE_CONTENT: {
        "description": "Ошибка валидации query-параметров (неверный формат)",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "loc": ["query", "name"],
                            "msg": "string does not match pattern",
                            "type": "value_error.str.regex"
                        }
                    ],
                    "status": 422,
                    "code": "VAL-422"
                }
            }
        }
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
}
)
async def get_exercises(
    response: Response,
    body: ExerciseQuery = Depends(),
    service: ExerciseService = Depends(get_exercise_service),
    user: UserBase = Depends(get_current_user)
):
    
    try:
        results = await service.get_exercise_by_get(
            name=body.name,
            description=body.description,
            category=body.category,
            muscle_group=body.muscle_group
        )
        
        count = len(results)
        reason = "Успешно найдены упражнения" if count > 0 else 'Ничего не найдено'
        
        return API_response(
            status_code=status.HTTP_200_OK if count > 0 else status.HTTP_404_NOT_FOUND,
            success=True,
            data=results,
            meta=construct_meta(
                reason=reason,
                other={
                    "total_count": count,
                    "filters": {
                        "name": body.name,
                        "description": body.description,
                        "category": body.category,
                        "muscle_group": body.muscle_group
                    }
                }
            ),
            response=response
        )
        
    except ValueError as e:
        logger.warning(f"Ошибка фильтрации: {e}")
        return API_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            data=None,
            meta=construct_meta(
                reason="Неверные значения фильтров",
                other={"error": str(e)}
            ),
            response=response
        )
    except (NotFoundError, Exception):
        raise

@router.get(
    '/{exercise_id}',
    summary="Получить упражнение по ID",
    description="Получение детальной информации об упражнении по его идентификатору.",
    response_description="Данные упражнения",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(ExerciseInDatabase),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def get_exercise_by_id(
    exercise_id: int,
    response: Response,
    service: ExerciseService = Depends(get_exercise_service),
    user: UserBase = Depends(get_current_user)
):
    
    try:
        result = await service.get_exercise_by_get(id=exercise_id)
        
        if not result:
            return API_response(
                status_code=status.HTTP_404_NOT_FOUND,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Упражнение не найдено",
                    other={"exercise_id": exercise_id}
                ),
                response=response
            )
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=result,
            meta=construct_meta(
                reason="Найдено упражнение",
                other={"exercise_id": exercise_id}
            ),
            response=response
        )
    
    except (NotFoundError, Exception):
        raise