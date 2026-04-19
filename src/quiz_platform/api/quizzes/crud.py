from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import List
from src._core.schemas import UserInDB, ErrorResponse
from src._core.exceptions import NotFoundError

from src.quiz_platform.config import QUIZ_PREFIX, QUIZ_TAGS
from src.quiz_platform.api.dependencies import get_current_user
from src.quiz_platform.local_core.schemas import QuizCreate, QuizResponse, Publish
from src.quiz_platform.local_core.service import get_quiz_service, QuizService

from src._core.response import API_response, construct_meta, ResponseData

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
    '/',
    summary="Создать новую викторину",
    description="""
    Создание викторины с набором вопросов и вариантов ответов.
    
    **Процесс:**
    1. Валидация входных данных (название, описание, список вопросов)
    2. Проверка существования викторины с таким названием
    3. Сохранение викторины в БД
    4. Привязка вопросов и вариантов ответов
    5. Возврат созданной викторины с ID
    
    **Требования:**
    - Авторизация пользователя
    - Минимум один вопрос
    - У каждого вопроса минимум 2 варианта ответа
    - Хотя бы один правильный ответ на вопрос
    """,
    response_description="Созданная викторина с деталями",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(
            List[QuizResponse],
            example={
                "id": 1,
                "name": "Python Basics",
                "description": "Тест по основам Python",
                "status": "draft",
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
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "At least one question is required",
                "status": 400,
                "code": "QZ-400"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(
            ErrorResponse,
            example={
                "detail": "Quiz with id 10 not found",
                "status": 404,
                "code": "QZ-404"
            }
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def create_quiz(
    body: QuizCreate,
    service: QuizService = Depends(get_quiz_service),
    user: UserInDB = Depends(get_current_user)    
) -> JSONResponse:
    
    try:
        result = await service.create_quiz(
            data=body,
            user_id=user.id
        )
        return API_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            data=result.to_dict(),
            meta=construct_meta(reason='Викторина успешно создана')
        )
    except (NotFoundError, Exception):
        raise


@router.put(
    '/{quiz_id}/publish',
    summary="Опубликовать или снять с публикации викторину",
    description="""
    Изменение статуса викторины.
    
    **Статусы:**
    - `draft` - черновик (недоступен для прохождения)
    - `published` - опубликован (доступен для прохождения)
    
    **Требования:**
    - Авторизация пользователя
    - Пользователь должен быть владельцем викторины
    - Викторина должна существовать
    - Для публикации требуется минимум 1 вопрос
    """,
    response_description="Обновлённая викторина",
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
                ]
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Cannot publish quiz without questions",
                "status": 400,
                "code": "QZ-400"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_403_FORBIDDEN: ResponseData.status_403(
            ErrorResponse,
            example={
                "detail": "You are not the owner of this quiz",
                "status": 403,
                "code": "ACCESS_DENIED"
            }
        ),
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
async def publish_quiz(
    quiz_id: int,
    publish_data: Publish,
    service: QuizService = Depends(get_quiz_service),
    user: UserInDB = Depends(get_current_user)   
) -> JSONResponse:
    try:
        result = await service.set_publish(
            publish=publish_data.publish,
            quiz_id=quiz_id,
            user_id=user.id
        )

        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=True,
            meta=construct_meta(
                reason=f'Викторина {"опубликована" if publish_data.publish == "published" else "сохранена как черновик"}'
            )
        )
    except Exception:
        raise
