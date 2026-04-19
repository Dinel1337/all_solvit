from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import List
from datetime import date
from collections import defaultdict
from src._core.schemas import UserInDB, ErrorResponse
from src._core.exceptions import NotFoundError 

from src.api_tracker.config import REPORTS_PREFIX, REPORTS_TAGS
from src.api_tracker.api.dependencies import get_current_user
from src.api_tracker.local_core.schemas import SummaryResponse, DateRangeQuery, DailyProgressResponse
from src.api_tracker.local_core.service import get_exercise_service, ExerciseService

from src._core.response import API_response, construct_meta, ResponseData

router = APIRouter(
    prefix=REPORTS_PREFIX,
    tags=REPORTS_TAGS,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(List[SummaryResponse]),
        status.HTTP_200_OK: ResponseData.status_200(List[SummaryResponse]),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

@router.get(
    '/summary',
    summary="Сводка по тренировкам за период",
    description="""
    Получение агрегированной статистики по тренировкам за указанный период.

    **Что возвращает:**
    - `workouts_done` – количество выполненных тренировок
    - `total_sets` – общее количество подходов
    - `total_reps` – общее количество повторений
    - `total_volume` – общий поднятый вес (сеты × повторения × вес)

    **Параметры:**
    - `from_date` – начальная дата (включительно, формат YYYY-MM-DD)
    - `to_date` – конечная дата (включительно, формат YYYY-MM-DD)
    """,
    response_description="Сводная статистика",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(SummaryResponse),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Дата 'from_date' не может быть позже 'to_date'",
                "status": 400,
                "code": "RPT-400"
            }
        )
    }
)
async def get_workout_summary(
    q: DateRangeQuery = Depends(),
    service: ExerciseService = Depends(get_exercise_service),
    user: UserInDB = Depends(get_current_user)
) -> JSONResponse:
    try:
        if q.from_date > q.to_date:
            return API_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Дата 'from_date' не может быть позже 'to_date'",
                    other={"from_date": str(q.from_date), "to_date": str(q.to_date)}
                )
            )

        workouts = await service.get_workouts_by_date_range(
            user_id=user.id,
            start_date=q.from_date,
            end_date=q.to_date
        )

        workouts_done = len(workouts)
        total_sets = sum(e.sets for w in workouts for e in w.exercises)
        total_reps = sum(e.reps for w in workouts for e in w.exercises)
        total_volume = sum(e.sets * e.reps * (e.weight or 0) for w in workouts for e in w.exercises)

        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=SummaryResponse(
                from_date=q.from_date,
                to_date=q.to_date,
                workouts_done=workouts_done,
                total_sets=total_sets,
                total_reps=total_reps,
                total_volume=float(total_volume)
            ).model_dump(mode='json'),
            meta=construct_meta(reason="Статистика успешно получена")
        )
    except (NotFoundError, Exception):
        raise


@router.get(
    '/progress',
    summary=" Динамика прогресса по дням",
    description="""
    Получение дневной динамики объёма тренировок.

    **Что возвращает:**
    - `date` – дата тренировки
    - `volume` – общий объём (сумма сетов × повторений × вес)
    - `workouts` – количество тренировок в этот день

    **Параметры:**
    - `from_date` – начальная дата (включительно, формат YYYY-MM-DD)
    - `to_date` – конечная дата (включительно, формат YYYY-MM-DD)
    """,
    response_description="Дневная динамика прогресса",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(List[DailyProgressResponse]),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Дата 'from_date' не может быть позже 'to_date'",
                "status": 400,
                "code": "RPT-400"
            }
        )
    }
)
async def get_workout_progress(
    q: DateRangeQuery = Depends(),
    service: ExerciseService = Depends(get_exercise_service),
    user: UserInDB = Depends(get_current_user)
) -> JSONResponse:
    try:
        if q.from_date > q.to_date:
            return API_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Дата 'from_date' не может быть позже 'to_date'",
                    other={"from_date": str(q.from_date), "to_date": str(q.to_date)}
                )
            )

        workouts = await service.get_workouts_by_date_range(
            user_id=user.id,
            start_date=q.from_date,
            end_date=q.to_date
        )

        daily_data = defaultdict(lambda: {'volume': 0.0, 'workouts': 0})

        for workout in workouts:
            date_str = workout.completed_at.strftime('%Y-%m-%d')
            daily_data[date_str]['workouts'] += 1

            for exercise in workout.exercises:
                volume = exercise.sets * exercise.reps * (exercise.weight or 0)
                daily_data[date_str]['volume'] += volume

        result = [
            DailyProgressResponse(
                date=date.fromisoformat(date_str),
                volume=data['volume'],
                workouts=data['workouts']
            )
            for date_str, data in sorted(daily_data.items())
        ]

        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=[item.model_dump(mode='json') for item in result],
            meta=construct_meta(
                reason="Динамика успешно получена",
                other={"total_days": len(result)}
            )
        )
    except (NotFoundError, Exception):
        raise