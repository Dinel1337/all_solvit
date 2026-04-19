from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from typing import Optional, List
from sqlalchemy.exc import IntegrityError

from src._core.exceptions import NotFoundError
from src._core.schemas import UserBase, ErrorResponse
from src.api_tracker.local_core.schemas import CreateCategory, CategoryInDatabase
from src.api_tracker.local_core.service import ExerciseService, get_exercise_service
from src._core.response import API_response, construct_meta, ResponseData
from ..dependencies import get_current_user
from ...config import CATEGORIES_PREFIX, CATEGORIES_TAGS

import logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=CATEGORIES_PREFIX,
    tags=CATEGORIES_TAGS,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(List[CategoryInDatabase]),
        status.HTTP_201_CREATED: ResponseData.status_201(CategoryInDatabase),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

# ==================== POST ====================
@router.post(
    '/',
    summary="Создать новую категорию",
    description="""
    Создание новой категории в базе данных.
    """,
    response_description="Созданная категория",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(
            CategoryInDatabase,
            example={
                "id": 1,
                "name": "силовые",
                "description": "Силовые упражнения"
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Category already exists",
                "status": 400,
                "code": "CAT-400"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def add_category(
    body: CreateCategory,
    response: Response,
    service: ExerciseService = Depends(get_exercise_service),
    user: UserBase = Depends(get_current_user)
) -> JSONResponse:
    
    try:
        result = await service.create_record(body, model_type='category')
        
        if result:
            return API_response(
                status_code=status.HTTP_201_CREATED,
                success=True,
                data=CategoryInDatabase.model_validate(result),
                meta=construct_meta(
                    reason="Категория создана успешно",
                    other={"category_id": result.id if hasattr(result, 'id') else None}
                ),
                response=response
            )
        else:
            return API_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Категория не создана",
                    other={"error": "Unknown error"}
                ),
                response=response
            )
    
    except (ValueError, IntegrityError) as e:
        logger.warning(f"Ошибка создания категории: {e}")
        return API_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            data=None,
            meta=construct_meta(
                reason="Неправильные данные или категория уже существует",
                other={"error": str(e.detail) if hasattr(e, 'detail') else str(e)}
            ),
            response=response
        )
    except (NotFoundError, Exception):
        raise


# ==================== GET ====================
@router.get(
    '/',
    summary="Получить список категорий",
    description="""
    Получение списка категорий.
    """,
    response_description="Список категорий",
    status_code=status.HTTP_200_OK
)
async def get_categories(
    response: Response,
    name: Optional[str] = None,
    description: Optional[str] = None,
    service: ExerciseService = Depends(get_exercise_service),
    user: UserBase = Depends(get_current_user)
):
    
    try:
        results = await service.get_recorg_by_service(
            name,
            description,
            model_type='category'
        )
        
        if results is None:
            categories = []
        elif isinstance(results, list):
            categories = [CategoryInDatabase.model_validate(r) for r in results]
        else:
            categories = [CategoryInDatabase.model_validate(results)]
        
        count = len(categories)
        reason = "Успешно найдены категории" if count > 0 else 'Ничего не найдено'
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=categories,
            meta=construct_meta(
                reason=reason,
                other={
                    "total_count": count,
                    "filters": {
                        "name": name,
                        "description": description
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