from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from typing import Optional, List
from ...config import MUSCLES_PREFIX, MUSCLES_TAGS
from sqlalchemy.exc import IntegrityError

from src._core.exceptions import AppException, NotFoundError
from src._core.schemas import UserBase, ErrorResponse
from src.api_tracker.local_core.schemas import CreateMuscle, MuscleInDatabase
from src.api_tracker.local_core.service import ExerciseService, get_exercise_service
from src._core.response import API_response, construct_meta, ResponseData
from ..dependencies import get_current_user

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=MUSCLES_PREFIX,
    tags=MUSCLES_TAGS,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(List[MuscleInDatabase]),
        status.HTTP_201_CREATED: ResponseData.status_201(MuscleInDatabase),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

# ==================== POST ====================
@router.post(
    '/',
    summary="Создать новую группу мышц",
    description="""
    Создание новой группы мышц в базе данных.
    """,
    response_description="Созданная группа мышц",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(
            MuscleInDatabase,
            example={
                "id": 1,
                "name": "Грудные",
                "description": "Грудные мышцы, жим лёжа, отжимания"
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Такая группа уже существует",
                "status": 400,
                "code": "MUSCLE-400"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def add_muscle(
    body: CreateMuscle,
    response: Response,
    service: ExerciseService = Depends(get_exercise_service),
    user: UserBase = Depends(get_current_user)
) -> JSONResponse:
    
    try:
        result = await service.create_record(body, model_type='muscle')
        
        if result:
            return API_response(
                status_code=status.HTTP_201_CREATED,
                success=True,
                data=MuscleInDatabase.model_validate(result),
                meta=construct_meta(
                    reason="Группа мышц создана успешно",
                    other={"muscle_id": result.id if hasattr(result, 'id') else None}
                ),
                response=response
            )
        else:
            return API_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Группа мышц не создана",
                    other={"error": "Unknown error"}
                ),
                response=response
            )
    
    except (ValueError, IntegrityError) as e:
        logger.warning(f"Ошибка создания группы мышц: {e}")
        return API_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            success=False,
            data=None,
            meta=construct_meta(
                reason="Неправильные данные или группа мышц уже существует",
                other={"error": str(e.detail) if hasattr(e, 'detail') else str(e)}
            ),
            response=response
        )
    except (NotFoundError, Exception):
        raise


# ==================== GET ====================
@router.get(
    '/',
    summary="Получить список групп мышц",
    description="""
    Получение списка всех групп мышц с возможностью фильтрации по названию и описанию.
    """,
    response_description="Список групп мышц",
    status_code=status.HTTP_200_OK
)
async def get_muscles(
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
            model_type='muscle'
        )
        
        if results is None:
            muscles = []
        elif isinstance(results, list):
            muscles = [MuscleInDatabase.model_validate(r) for r in results]
        else:
            muscles = [MuscleInDatabase.model_validate(results)]
        
        count = len(muscles)
        reason = "Успешно найдены группы мышц" if count > 0 else 'Ничего не найдено'
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=muscles,
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
        logger.warning(f"Ошибка фильтрации групп мышц: {e}")
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