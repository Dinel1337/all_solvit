import logging
from fastapi import APIRouter, status, Depends, Response
from src.config import AUTH_PREFIX, AUTH_TAGS

from sqlalchemy.ext.asyncio import AsyncSession

from src._core.auth import create_access_token
from src._core.schemas import UserLogin, UserLoginResponse, ErrorResponse
from src._core.exceptions import UserEmailExistsException, NotFoundError
from src._core.response import API_response, construct_meta, ApiResponse, ResponseData
from src._core.repositories import UserRepository

from src._core.database import get_db

from global_config import CookieSetter

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=AUTH_PREFIX,
    tags=AUTH_TAGS,
    responses={
        status.HTTP_202_ACCEPTED: ResponseData.status_202(UserLoginResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

@router.post(
    '/login',
    summary='Вход в аккаунт',
    description="""
    Аутентификация пользователя и получение JWT токена.
    
    **Процесс:**
    1. Проверка email и пароля
    2. Генерация JWT токена
    3. Установка cookie с токеном
    4. Возврат токена в теле ответа
    
    **Токен используется:**
    - В cookie: `access_token`
    - В заголовке: `Authorization: Bearer <token>`
    """,
    response_description="Успешная аутентификация",
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_202_ACCEPTED: ResponseData.status_202(UserLoginResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(
            ErrorResponse, 
            example={
                        "wrong_password": {
                            "summary": "Неверный пароль",
                            "value": {
                                "detail": "Invalid password",
                                "status": 401,
                                "code": "AUTH-401"
                            }
                        },
                        "user_not_found": {
                            "summary": "Пользователь не найден",
                            "value": {
                                "detail": "User not found",
                                "status": 401,
                                "code": "AUTH-401"
                            }
                        }
                    }
            ),
        status.HTTP_429_TOO_MANY_REQUESTS: ResponseData.status_429()
    }
)
async def login_user(
    response: Response,
    body: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> ApiResponse[UserLoginResponse]:
    from src._core.services import UserService
    service = UserService(UserRepository(db))
    data = None
    
    try:
        data = await service.check_user_base(body.username, password=body.password)
        token = create_access_token(data.id)

        response.set_cookie(
            key='access_token',
            value=token,
            secure=CookieSetter.SECURE,
            httponly=CookieSetter.HTTPONLY,
            samesite=CookieSetter.SAMESITE,
            max_age=CookieSetter.MAX_AGE
        )
        
        return API_response(
            status_code=status.HTTP_202_ACCEPTED, 
            success=True, 
            data=data, 
            meta=construct_meta(
                reason="Успешный вход в сессию", 
                other={'token': token}
            ),
            response=response
        )
    
    except (UserEmailExistsException, NotFoundError) as e:
        raise
    
    except Exception as e:
        raise