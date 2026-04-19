from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import List
from src._core.schemas import UserInDB, ErrorResponse
from src._core.exceptions import NotFoundError 

from src.api_tracker.config import WORKOUT_TAGS, WORKOUT_PREFIX
from src.api_tracker.api.dependencies import get_current_user
from src.api_tracker.local_core.schemas import WorkoutCreate, WorkoutFilters, WorkoutResponse
from src.api_tracker.local_core.service import get_exercise_service, ExerciseService

from src._core.response import API_response, construct_meta, ResponseData

router = APIRouter(
    prefix=WORKOUT_PREFIX,
    tags=WORKOUT_TAGS,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(List[WorkoutResponse]),
        status.HTTP_200_OK: ResponseData.status_200(List[WorkoutResponse]),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

@router.post(
    '/',
    summary="Создать новую тренировку",
    description="""
    Создание тренировки с набором упражнений.
    
    **Процесс:**
    1. Валидация входных данных (название, описание, список упражнений)
    2. Проверка существования упражнений (по ID или названию)
    3. Сохранение тренировки в БД
    4. Привязка упражнений к тренировке
    5. Возврат созданной тренировки с ID
    
    **Требования:**
    - Авторизация пользователя
    - Минимум одно упражнение в списке
    - Упражнения должны существовать в базе
    """,
    response_description="Созданная тренировка с деталями",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(
            List[WorkoutResponse],
            example={
                "id": 1,
                "name": "Тренировка груди",
                "description": "Интенсивная тренировка на грудные мышцы",
                "user_id": 123,
                "exercises": [
                    {"exercise_id": 5, "sets": 3, "reps": 10},
                    {"exercise_id": 8, "sets": 4, "reps": 8}
                ],
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T10:30:00"
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "At least one exercise is required",
                "status": 400,
                "code": "WO-400"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(
            ErrorResponse,
            example={
                "detail": "Exercise with id 10 not found",
                "status": 404,
                "code": "WO-404"
            }
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def create_workout(
    body: WorkoutCreate,
    service: ExerciseService = Depends(get_exercise_service),
    user: UserInDB = Depends(get_current_user)    
) -> JSONResponse:
    
    try:
        exercises_data = [ex.model_dump() for ex in body.exercises]
        result = await service.create_workout(
            name=body.name,
            user_id=user.id,
            exercises_data=exercises_data,
            description=body.description
        )
        return API_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            data=WorkoutResponse.model_validate(result).model_dump(mode='json'),
            meta=construct_meta(reason='Тренировка успешно создана')
        )
    except (NotFoundError, Exception):
        raise


@router.get(
    '/',
    summary="Получить список тренировок пользователя",
    description="""
    Получение тренировок текущего пользователя с возможностью фильтрации.
    
    **Параметры фильтрации:**
    - `limit` - максимальное количество тренировок (по умолчанию 10, максимум 100)
    
    **Сортировка:** по дате создания (новые сверху)
    
    **Примеры:**
    - `GET /workouts/` - последние 10 тренировок
    - `GET /workouts/?limit=25` - последние 25 тренировок
    """,
    response_description="Список тренировок пользователя",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            List[WorkoutResponse],
            example={
                "data": [
                    {
                        "id": 1,
                        "name": "Тренировка груди",
                        "description": "...",
                        "created_at": "2025-01-15T10:30:00"
                    }
                ],
                "meta": {
                    "total_count": 15,
                    "limit": 10
                }
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def get_workouts(
    q: WorkoutFilters = Depends(),
    service: ExerciseService = Depends(get_exercise_service),
    user: UserInDB = Depends(get_current_user)    
) -> JSONResponse:
    
    try:
        result = await service.get_user_workouts(
            user_id=user.id,
            limit=q.limit
        )
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=[
            WorkoutResponse.model_validate(w).model_dump(mode='json') 
            for w in result
        ],
            meta=construct_meta(reason='Тренировки найдены')
        )
    except (NotFoundError, Exception):
        raise


@router.get(
    '/{workout_id}',
    summary="Получить тренировку по ID",
    description="""
    Получение детальной информации о конкретной тренировке.
    
    **Возвращает:**
    - Информацию о тренировке (название, описание, дата)
    - Список упражнений с подходами, повторениями и весами
    - ID пользователя, которому принадлежит тренировка
    
    **Проверки:**
    - Тренировка должна существовать
    - Тренировка должна принадлежать текущему пользователю
    """,
    response_description="Детальная информация о тренировке",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            WorkoutResponse,
            example={
                "id": 1,
                "name": "Тренировка груди",
                "description": "Интенсивная тренировка",
                "user_id": 123,
                "completed_at": "2025-01-15T10:30:00",
                "exercises": [
                    {
                        "id": 1,
                        "exercise_id": 5,
                        "exercise_name": "Жим лежа",
                        "sets": 3,
                        "reps": 10,
                        "weight": 50.5,
                        "order": 1
                    }
                ]
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(
            ErrorResponse,
            example={
                "detail": "Workout with id 1 not found",
                "status": 404,
                "code": "WO-404"
            }
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def get_workout_by_id(
    workout_id: int,
    service: ExerciseService = Depends(get_exercise_service),
    user: UserInDB = Depends(get_current_user)    
) -> JSONResponse:
    
    try:
        result = await service.get_workout_by_id(workout_id)
        
        if result.user_id != user.id:
            return API_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                data=None,
                meta=construct_meta(reason='Нет доступа к этой тренировке')
            )
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=WorkoutResponse.model_validate(result).model_dump(mode='json'),
            meta=construct_meta(reason='Тренировка найдена')
        )
    except (NotFoundError, Exception):
        raise