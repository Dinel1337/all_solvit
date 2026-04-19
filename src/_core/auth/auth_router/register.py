import logging
from fastapi import APIRouter, status, Depends, Response
from fastapi.responses import JSONResponse
from src.config import AUTH_PREFIX, AUTH_TAGS

from src._core.schemas import UserCreate, ErrorResponse, UserCreateResponse 
from sqlalchemy.ext.asyncio import AsyncSession
from src._core.database import get_db
from src._core.exceptions import UserEmailExistsException
from src._core.response import API_response, construct_meta, ResponseData
from src._core.repositories import UserRepository
from src._core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix=AUTH_PREFIX,
    tags=AUTH_TAGS,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(UserCreateResponse),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(ErrorResponse),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)

@router.post(
    '/register',
    summary='Регистрация аккаунта',
    description="""
    Регистрация нового пользователя.
    
    **Процесс:**
    1. Проверка уникальности email/username
    2. Хэширование пароля
    3. Создание пользователя в БД
    4. Возврат данных пользователя
    
    **Требования:**
    - username: от 3 до 50 символов
    - email: валидный email
    - password: минимум 6 символов
    """,
    response_description="Пользователь успешно создан",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: ResponseData.status_201(
            UserCreateResponse,
            example={
                "username": "john_doe",
                "email": "john@example.com",
                "id": 1,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ),
        status.HTTP_401_UNAUTHORIZED: ResponseData.status_401(
            ErrorResponse,
            example={
                "email_exists": {
                    "summary": "Email уже существует",
                    "value": {
                        "detail": "User with this email already exists",
                        "status": 401,
                        "code": "AUTH-401"
                    }
                },
                "username_exists": {
                    "summary": "Username уже существует",
                    "value": {
                        "detail": "Username already taken",
                        "status": 401,
                        "code": "AUTH-401"
                    }
                }
            }
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: ResponseData.status_500()
    }
)
async def register_user(
    response: Response,
    body: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> JSONResponse:
    from src._core.services import UserService
    service = UserService(UserRepository(db))
    data = None
    
    try:
        data = await service.create_user(body)
        
        logger.info(f'Создан пользователь: {data.username}')
        
        return API_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            data=data,
            meta=construct_meta(
                reason="Пользователь успешно создан",
                other={"user_id": data.id}
            ),
            response=response
        )
    
    except UserEmailExistsException as e:
        logger.warning(f'Ошибка регистрации: {e.detail}')
        return API_response(
            status_code=e.status_code,
            success=False,
            data=None,
            meta=construct_meta(
                reason="Ошибка регистрации",
                other={"error": e.detail}
            ),
            response=response
        )
    
    except Exception:
        raise