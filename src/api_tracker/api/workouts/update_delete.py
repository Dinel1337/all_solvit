from fastapi import APIRouter, Depends, status, Path
from fastapi.responses import JSONResponse

from src._core.schemas import UserInDB, ErrorResponse
from src._core.response import API_response, construct_meta, ResponseData
from src._core.exceptions import NotFoundError

from src.api_tracker.config import WORKOUT_TAGS, WORKOUT_PREFIX
from src.api_tracker.api.dependencies import get_current_user
from src.api_tracker.local_core.schemas import WorkoutUpdate, WorkoutResponse
from src.api_tracker.local_core.service import get_exercise_service, ExerciseService

router = APIRouter(
    prefix=WORKOUT_PREFIX,
    tags=WORKOUT_TAGS,
    responses={
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_403_FORBIDDEN: ResponseData.status_403(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)


@router.patch(
    '/{workout_id}',
    summary="Изменить тренировку",
    description="""
    Частичное обновление тренировки.

    **Можно изменить:**
    - `name` – название тренировки
    - `description` – описание
    - `completed_at` – дата выполнения

    **Пример запроса:**
    ```json
    {
        "name": "Новое название",
        "description": "Новое описание",
        "completed_at": "2026-04-04T10:00:00"
    }
Проверки:

Тренировка должна существовать

Тренировка должна принадлежать текущему пользователю
""",
    response_description="Обновлённая тренировка",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            WorkoutResponse,
            example={
                "id": 1,
                "name": "Новое название",
                "description": "Новое описание",
                "user_id": 123,
                "completed_at": "2026-04-04T10:00:00",
                "exercises": [
                    {
                        "id": 1,
                        "exercise_id": 5,
                        "sets": 3,
                        "reps": 10,
                        "weight": 50.5,
                        "order": 1
                    }
                ]
            }
        ),
        status.HTTP_403_FORBIDDEN: ResponseData.status_403(
            ErrorResponse,
            example={
                "detail": "Нет доступа к этой тренировке",
                "status": 403,
                "code": "FORBIDDEN"
            }
        ),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(
            ErrorResponse,
            example={
                "detail": "Тренировка с id 1 не найдена",
                "status": 404,
                "code": "WO-404"
            }
        )
    }
)
async def update_workout(
    body: WorkoutUpdate,
    workout_id: int = Path(..., ge=1, description="ID тренировки"),
    service: ExerciseService = Depends(get_exercise_service),
    user: UserInDB = Depends(get_current_user)
) -> JSONResponse:
    try:
        existing = await service.get_workout_by_id(workout_id)

        if existing.user_id != user.id:
            return API_response(
                status_code=status.HTTP_403_FORBIDDEN,
                success=False,
                data=None,
                meta=construct_meta(reason='Нет доступа к этой тренировке')
            )

        result = await service.update_workout(
            workout_id=workout_id,
            name=body.name,
            description=body.description,
            completed_at=body.completed_at
        )

        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=WorkoutResponse.model_validate(result).model_dump(mode='json'),
            meta=construct_meta(reason='Тренировка успешно обновлена')
        )

    except (NotFoundError, Exception):
        raise


@router.delete(
    '/{workout_id}',
    summary="Удалить тренировку",
    description="""
    Полное удаление тренировки.
    
    ### Что происходит
    - Удаляется запись тренировки из таблицы `workouts`
    - Удаляются все связанные записи из `workout_exercises`
    
    ### Проверки
    - Тренировка должна существовать
    - Тренировка должна принадлежать текущему пользователю
    """,
    response_description="Тренировка удалена",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: ResponseData.status_204(),
        status.HTTP_403_FORBIDDEN: ResponseData.status_403(
            ErrorResponse,
            example={
                "detail": "Нет доступа к этой тренировке",
                "status": 403,
                "code": "FORBIDDEN"
            }
        ),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(
            ErrorResponse,
            example={
                "detail": "Тренировка с id 1 не найдена",
                "status": 404,
                "code": "WO-404"
            }
        )
    }
)
async def delete_workout(
    workout_id: int = Path(..., ge=1, description="ID тренировки"),
    service: ExerciseService = Depends(get_exercise_service),
    user: UserInDB = Depends(get_current_user)
) -> None:
    
    existing = await service.get_workout_by_id(workout_id)

    if existing.user_id != user.id:
        return API_response(
            status_code=status.HTTP_403_FORBIDDEN,
            success=False,
            data=None,
            meta=construct_meta(reason='Нет доступа к этой тренировке')
        )

    await service.delete_workout(workout_id)
    
    return None