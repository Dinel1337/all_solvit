import logging
from fastapi import APIRouter, status, Depends

from src._core.schemas import UserInDB, ErrorResponse
from src._core.exceptions import UserBadParametrError, NotFoundError
from src._core.response import API_response, construct_meta, ResponseData
from src._core.auth import get_current_user
from src.config import USERS_PREFIX, USERS_TAGS

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=USERS_PREFIX,
    tags=USERS_TAGS,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(UserInDB),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

@router.get(
    '/me',
    summary='Получить профиль текущего пользователя',
    description="""
    Получение информации о текущем авторизованном пользователе.
    
    **Процесс:**
    1. Автоматическое извлечение и валидация токена из cookie `access_token`
    2. Поиск пользователя в базе данных
    3. Возврат данных профиля
    
    **Требования:**
    - Наличие валидного `access_token` в cookie
    - Токен не должен быть просрочен или отозван
    """,
    response_description="Данные пользователя",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: ResponseData.status_200(
            UserInDB,
            example={
                "email": "user@example.com",
                "username": "username",
                "id": 1,
                "status_operation": "created"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(
            ErrorResponse,
            example={
                "invalid_token": {
                    "summary": "Недействительный токен",
                    "value": {
                        "detail": "Invalid or expired token",
                        "status": 401,
                        "code": "AUTH-401"
                    }
                },
                "token_missing": {
                    "summary": "Отсутствует токен",
                    "value": {
                        "detail": "Token not found",
                        "status": 401,
                        "code": "AUTH-401"
                    }
                }
            }
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

async def profile(
    user: UserInDB = Depends(get_current_user)
) :
    """
    Получить профиль текущего пользователя.
    
    Возвращает данные пользователя при успешной авторизации.
    """
    try:
        return API_response(
            status_code=status.HTTP_200_OK,
            success=True,
            data=user.model_dump(mode='json'),
            meta=construct_meta(
                reason="Профиль успешно получен",
                other={"user_id": user.id}
            )
        )
    except (UserBadParametrError, NotFoundError) as e:
        logger.warning(f"Ошибка получения профиля: {e}")
        return API_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            success=False,
            data=None,
            meta=construct_meta(
                reason="Ошибка авторизации",
                other={"error": str(e)}
            )
        )
    
    except Exception:
        raise