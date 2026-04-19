from ..repositories import UserRepository
from ..schemas import UserCreate, UserInDB
from ..exceptions import UserNotFound, UserErrorCreateException, UserEmailExistsException, UserBadParametrError, PasswordValidationError
from ..enum import OperationUserStatus
from ..models.user_models import AccessToken, RefreshToken 
from ..utils import crypt_pass, verify_password
from ..auth.jwt import create_access_token, create_refresh_token
from ..models import User

from typing import Optional

from datetime import datetime, timedelta, timezone
from global_config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

import logging
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def create_user(
        self,
        user_create: UserCreate
        ) -> UserInDB:

        if await self.repository.get_by_email(user_create.email):
            raise UserEmailExistsException(user_create.email)
        
        if await self.repository.get_by_username(user_create.username):
            raise UserEmailExistsException(f"Username {user_create.username} already exists")
        # expires_at_access = datetime.now(timezone.utc) + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
        # expires_at_refresh = datetime.now(timezone.utc) + timedelta(REFRESH_TOKEN_EXPIRE_DAYS)

        password_hash = crypt_pass(user_create.password)

        user = await self.repository.create_user({
            "email": user_create.email,
            "username": user_create.username,
            "password_hash": password_hash
        })

        # access_token = await self.repository.create_token({
        #     "user_id": user.id,
        #     "access_token": create_access_token(user.id),
        #     "expires_at": expires_at_access
        # }, AccessToken)

        # refresh_token = await self.repository.create_token({
        #     "user_id": user.id,
        #     "refresh_token": create_refresh_token(user.id),
        #     "expires_at": expires_at_refresh
        # }, RefreshToken)

        if not user:
            raise UserErrorCreateException(username=user_create.username)
        
        user_data = vars(user)
        user_data["status_operation"] = OperationUserStatus.CREATED
        
        return UserInDB.model_validate(user_data)
    
    async def delete_user(
        self, 
        user_id: int
        ) -> bool:
        result = await self.repository.delete_user_in_base(user_id)
        return True
    
    async def check_user_base(
        self,
        username: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None 
    ) -> UserInDB:
        
        if not (identifier := email or username):
            raise UserBadParametrError()
        
        method = self.repository.get_by_email if email else self.repository.get_by_username
        user = await method(identifier)
        if user is None:
            raise UserNotFound(identifier, message='Пользователь не найден')
        pas = None
        if user and password:
            pas = verify_password(password, user.password_hash)
            if pas:
                
                expires_at_access = datetime.now(timezone.utc) + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
                expires_at_refresh = datetime.now(timezone.utc) + timedelta(REFRESH_TOKEN_EXPIRE_DAYS)

                access_token = await self.repository.create_token({
                "user_id": user.id,
                "access_token": create_access_token(user.id),
                "expires_at": expires_at_access
                    }, AccessToken)

                refresh_token = await self.repository.create_token({
                    "user_id": user.id,
                    "refresh_token": create_refresh_token(user.id),
                    "expires_at": expires_at_refresh
                }, RefreshToken)

                return UserInDB.model_validate(user)
            raise PasswordValidationError('Неправильный пароль')

    async def get_user(self,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    )-> User | None:
        if token:
            result = await self.repository.get_user_by_access_token(token)
        elif user_id:
            # assert user_id is not None # для Pylance флажочек
            result = await self.repository.get_by_id(user_id)
        else:
            raise UserBadParametrError()
        return result
        

    async def token_manipulated(
        self,
        token: str,
        info: bool = False,
        delete: bool = False,
        save: bool = False
    ) -> Optional[AccessToken] | bool:
        """
        Управление токеном

        Returns:
            - info=True: возвращает объект токена или None
            - delete=True: возвращает bool (успешно удалён или нет)
        
        """
        try:
            token_info = await self.repository.check_token_info_access_token(token)

            if info:
                return token_info

            if delete:
                if token_info and hasattr(token_info, 'id'):
                    result = await self.repository.delete_token_info_access_token(token_info)
                    return result is not None
                return False

            if save:
                # TODO:
                pass
            
            return False
        except:
            raise UserNotFound(token, search_field='token')