from fastapi import APIRouter, Depends, status, Path
from fastapi.responses import JSONResponse
from typing import List

from src._core.schemas import UserInDB, ErrorResponse
from src._core.response import API_response, construct_meta, ResponseData
from src._core.exceptions import NotFoundError

from src.quiz_platform.config import QUIZ_PREFIX, QUIZ_TAGS
from src.quiz_platform.api.dependencies import get_current_user
from src.quiz_platform.local_core.schemas import QuizResponse, QuizFilters
from src.quiz_platform.local_core.service import get_quiz_service, QuizService


router = APIRouter(
    prefix=QUIZ_PREFIX,
    tags=QUIZ_TAGS,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(List[QuizResponse]),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)


@router.get(
    '/',
    summary="Получить список викторин",
    description="""
    Получение списка викторин с фильтрацией по поисковому запросу и пагинацией.
    
    **Параметры:**
    - `search` - поиск по названию или описанию (частичное совпадение)
    - `limit` - количество записей (по умолчанию 100)
    - `offset` - отступ для пагинации (по умолчанию 0)
    
    ВАЖНО! отображаются только опубликованные викторины
    """,
    response_description="Список викторин",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            List[QuizResponse],
            example=[
                {
                    "id": 1,
                    "name": "Python Basics",
                    "description": "Тест по основам Python",
                    "status": "published",
                    "author_id": 123,
                    "questions": []
                }
            ]
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def get_quizzes(
    filters: QuizFilters = Depends(),
    service: QuizService = Depends(get_quiz_service),
    user: UserInDB = Depends(get_current_user)
) -> JSONResponse:
    try:
        result = await service.get_quizzes(
            search=filters.search,
            limit=filters.limit,
            offset=filters.offset
        )
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=[quiz.to_dict() for quiz in result],
            meta=construct_meta(
                reason='Список викторин успешно получен',
                other={"limit": filters.limit, "offset": filters.offset, "total": len(result)}
            )
        )
    except (NotFoundError, Exception):
        raise


@router.get(
    '/{quiz_id}',
    summary="Получить викторину по ID",
    description="""
    Получение викторины с полной структурой вопросов и вариантов ответов.
    
    **Возвращает:**
    - Информацию о викторине (название, описание, статус)
    - Список вопросов с баллами и порядком
    - Варианты ответов с указанием правильных
    
    **Требования:**
    - Авторизация пользователя
    - Викторина должна существовать
    """,
    response_description="Полная структура викторины",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            QuizResponse,
            example={
                "id": 1,
                "name": "Python Basics",
                "description": "Тест по основам Python",
                "status": "published",
                "author_id": 123,
                "questions": [
                    {
                        "id": 1,
                        "text": "Что выведет print(2+2)?",
                        "points": 1,
                        "order": 0,
                        "options": [
                            {"id": 1, "text": "3", "is_correct": False},
                            {"id": 2, "text": "4", "is_correct": True}
                        ]
                    }
                ],
                "created_at": "2025-01-15T10:30:00",
                "updated_at": "2025-01-15T10:30:00"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(
            ErrorResponse,
            example={
                "detail": "Quiz with id 1 not found",
                "status": 404,
                "code": "QUIZ_NOT_FOUND"
            }
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def get_quiz(
    quiz_id: int = Path(ge=1),
    service: QuizService = Depends(get_quiz_service),
    user: UserInDB = Depends(get_current_user)
) -> JSONResponse:
    try:
        result = await service.get_quiz(quiz_id)
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=result.to_dict(),
            meta=construct_meta(reason='Викторина успешно получена')
        )
    except (NotFoundError, Exception):
        raise