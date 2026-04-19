from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
from src._core.schemas import UserInDB, ErrorResponse
from src._core.exceptions import NotFoundError

from src.quiz_platform.config import ATTEMPTS_PREFIX, ATTEMPTS_TAGS
from src.quiz_platform.api.dependencies import get_current_user
from src.quiz_platform.local_core.schemas import AnswersBulkCreate
from src.quiz_platform.local_core.service import get_quiz_service, QuizService

from src._core.response import API_response, construct_meta, ResponseData

router = APIRouter(
    prefix=ATTEMPTS_PREFIX,
    tags=ATTEMPTS_TAGS,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(dict),
        status.HTTP_201_CREATED: ResponseData.status_201(dict),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(ErrorResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_403_FORBIDDEN: ResponseData.status_403(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)


@router.put(
    '/{attempt_id}/answers',
    summary="Сохранить ответы на вопросы",
    description="""
    Массовое сохранение ответов пользователя на вопросы викторины.
    
    **Процесс:**
    1. Проверка существования попытки
    2. Проверка, что попытка не завершена
    3. Валидация каждого ответа (вопрос принадлежит квизу, вариант ответа принадлежит вопросу)
    4. Сохранение или обновление ответов
    
    **Требования:**
    - Попытка должна существовать
    - Попытка не должна быть завершена
    - Вопросы должны принадлежать викторине
    - Варианты ответов должны принадлежать соответствующим вопросам
    """,
    response_description="Сохранённые ответы",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            dict,
            example={
                "saved_count": 2,
                "answers": [
                    {"question_id": 1, "selected_option_id": 5},
                    {"question_id": 2, "selected_option_id": 8}
                ]
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Invalid answer for question 1",
                "status": 400,
                "code": "INVALID_ANSWER"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def save_answers(
    attempt_id: int,
    body: AnswersBulkCreate,
    service: QuizService = Depends(get_quiz_service),
    user: Optional[UserInDB] = Depends(get_current_user)
) -> JSONResponse:
    """
    Сохранить ответы пользователя на вопросы.
    """
    try:
        result = await service.save_answers_bulk(
            attempt_id=attempt_id,
            answers_data=body.answers
        )
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data={
                "saved_count": len(result),
                "answers": [
                    {"question_id": a.question_id, "selected_option_id": a.selected_option_id}
                    for a in result
                ]
            },
            meta=construct_meta(reason='Ответы успешно сохранены')
        )
    except (NotFoundError, Exception):
        raise


@router.post(
    '/{attempt_id}/finish',
    summary="Завершить прохождение викторины",
    description="""
    Завершение попытки прохождения викторины.
    
    **Процесс:**
    1. Проверка существования попытки
    2. Проверка, что попытка не завершена
    3. Подсчёт баллов на основе сохранённых ответов
    4. Сохранение итогового балла и времени завершения
    
    **Требования:**
    - Попытка должна существовать
    - Попытка не должна быть завершена
    """,
    response_description="Результат завершения",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            dict,
            example={
                "score": 8
            }
        ),
        status.HTTP_400_BAD_REQUEST: ResponseData.status_400(
            ErrorResponse,
            example={
                "detail": "Attempt already finished",
                "status": 400,
                "code": "ATTEMPT_ALREADY_FINISHED"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def finish_attempt(
    attempt_id: int,
    service: QuizService = Depends(get_quiz_service),
    user: Optional[UserInDB] = Depends(get_current_user)
) -> JSONResponse:
    """
    Завершить прохождение викторины.
    """
    try:
        result = await service.finish_attempt(attempt_id=attempt_id)
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data={'score': result},
            meta=construct_meta(reason='Викторина завершена', other={
                'score': result
            })
        )
    except (NotFoundError, Exception):
        raise


@router.get(
    '/{attempt_id}/result',
    summary="Получить результат прохождения",
    description="""
    Получение детального результата прохождения викторины.
    
    **Возвращает:**
    - Информацию о викторине
    - Общий балл и максимально возможный
    - Детальные ответы на каждый вопрос
    - Время начала и завершения
    
    **Требования:**
    - Попытка должна существовать
    """,
    response_description="Детальный результат прохождения",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            dict,
            example={
                "attempt_id": 1,
                "quiz_id": 1,
                "quiz_name": "Python Basics",
                "started_at": "2025-01-15T10:30:00",
                "finished_at": "2025-01-15T10:35:00",
                "total_score": 8,
                "max_possible_score": 10,
                "answers": [
                    {
                        "question_id": 1,
                        "question_text": "2+2=?",
                        "points": 2,
                        "selected_option_id": 5,
                        "is_correct": True,
                        "earned_points": 2
                    }
                ]
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_404_NOT_FOUND: ResponseData.status_404(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def get_attempt_result(
    attempt_id: int,
    service: QuizService = Depends(get_quiz_service),
    user: Optional[UserInDB] = Depends(get_current_user)
) -> JSONResponse:
    """
    Получить результат прохождения викторины.
    """
    try:
        result = await service.get_attempt_result(attempt_id=attempt_id)
        
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=result,
            meta=construct_meta(reason='Результат успешно получен')
        )
    except (NotFoundError, Exception):
        raise