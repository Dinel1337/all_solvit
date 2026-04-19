from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional, List

from src._core.schemas import UserInDB, ErrorResponse
from src._core.response import API_response, construct_meta, ResponseData
from src._core.exceptions import NotFoundError

from src.quiz_platform.config import QUIZ_PREFIX, QUIZ_TAGS
from src.quiz_platform.api.dependencies import get_current_user
from src.quiz_platform.local_core.service import get_quiz_service, QuizService
from src.quiz_platform.local_core.schemas import QuizResponse

router = APIRouter(
    prefix=QUIZ_PREFIX,
    tags=QUIZ_TAGS,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(List[QuizResponse]),
        status.HTTP_200_OK: ResponseData.status_200(List[QuizResponse]),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_403_FORBIDDEN: ResponseData.status_403(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)


@router.post(
    '/{quiz_id}/attempts',
    summary="Начать прохождение викторины",
    description="""
    Создание новой попытки прохождения викторины.
    
    **Процесс:**
    1. Проверка существования и публикации викторины
    2. Создание записи в таблице attempt
    3. Для авторизованных пользователей привязывается user_id
    4. Для неавторизованных генерируется anonymous_token
    
    **Требования:**
    - Викторина должна быть опубликована (status = 'published')
    - Викторина должна существовать
    """,
    response_description="Созданная попытка (ID и токен для анонимных)",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(
            dict,
            example={
                "attempt_id": 1,
                "anonymous_token": "550e8400-e29b-41d4-a716-446655440000"
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Quiz is not published",
                "status": 400,
                "code": "QUIZ_NOT_PUBLISHED"
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
async def create_attempt(
    quiz_id: int,
    service: QuizService = Depends(get_quiz_service),
    user: Optional[UserInDB] = Depends(get_current_user)
) -> JSONResponse:
    try:
        user_id = user.id if user else None
        attempt = await service.start_attempt(
            quiz_id=quiz_id,
            user_id=user_id,
            anonymous_token=None
        )
        
        response_data = {"attempt_id": attempt.id}
        if attempt.anonymous_token:
            response_data["anonymous_token"] = attempt.anonymous_token
        
        return API_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            data=response_data,
            meta=construct_meta(reason='Попытка успешно создана')
        )
    except (Exception, NotFoundError):
        raise