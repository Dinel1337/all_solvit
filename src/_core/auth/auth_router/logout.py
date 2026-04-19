import logging
from fastapi import APIRouter, status, Depends, Response, Cookie
from src.config import AUTH_PREFIX, AUTH_TAGS

from typing import Annotated
from global_config import CookieSetter
from sqlalchemy.ext.asyncio import AsyncSession
from src._core.schemas import ErrorResponse
from src._core.repositories import UserRepository
from src._core.response import API_response, construct_meta, ResponseData
from src._core.database import get_db
from src._core.database import get_db


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=AUTH_PREFIX,
    tags=AUTH_TAGS
)

@router.post(
    '/logout',
    summary='Выход из аккаунта',
    description="""
    Завершение сессии пользователя и удаление JWT токена.
    
    **Процесс:**
    1. Получение токена из cookie
    2. Инвалидация токена (добавление в черный список)
    3. Удаление cookie `access_token`
    4. Возврат подтверждения
    
    **Требования:**
    - Наличие валидного токена в cookie
    """,
    response_description="Успешный выход из системы",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: ResponseData.status_204(),
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
async def logout(
    response: Response,
    access_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db)
) ->  None:
    """
    Выход из аккаунта.
    
    - **token**: JWT токен из cookie
    
    При успешном выходе:
    - Токен инвалидируется
    - Удаляется cookie `access_token`
    - Возвращается статус 204 без тела
    """
    from src._core.services import UserService
    service = UserService(UserRepository(db))
    try:
        if not access_token:
            logger.warning("Попытка выхода без токена")
            return API_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Токен не предоставлен",
                    other={"error": "Token missing"}
                ),
                response=response
            )
        
        success = await service.token_manipulated(token=access_token, delete=True)
        
        if success:
            response.delete_cookie(
                key='access_token',
                secure=CookieSetter.SECURE,
                httponly=CookieSetter.HTTPONLY,
                samesite=CookieSetter.SAMESITE
            )
            logger.info(f"Успешный выход, токен инвалидирован")
            
            return None
        
        else:
            logger.warning(f"Попытка выхода с невалидным токеном")
            return API_response(
                status_code=status.HTTP_401_UNAUTHORIZED,
                success=False,
                data=None,
                meta=construct_meta(
                    reason="Недействительный токен",
                    other={"error": "Invalid token"}
                ),
                response=response
            )
    
    except Exception:
        raise