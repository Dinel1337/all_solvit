import logging

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import User, AccessToken, RefreshToken
from ..database import PublicBase
from ..exceptions import UserNotFound
from typing import Type 
from .main_repository import BaseRepository
from ..utils import RaiseControl

rc = RaiseControl(
    error_map={
        'user': UserNotFound
    }
)

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.UserBase = BaseRepository(session, User)
        self.AccessTokenBase = BaseRepository(session, AccessToken)
        self.RefreshTokenBase = BaseRepository(session, RefreshToken)
        
    @rc(exc='user')
    async def get_id_by_username(self, username: str) -> int | None:
        """Получить ID пользователя по имени"""
        return await self.UserBase.find_scalar_by(User.id, username=username)

    @rc(exc='user')
    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        return await self.UserBase.find_one_by(id=user_id)

    # @rc(exc='user', error_message='email не существует')  
    async def get_by_email(self, user_email: str) -> User | None:
        """Получить пользователя по email"""
        return await self.UserBase.find_one_by(email=user_email)

    # @rc(exc='user', error_message='Имя такого пользователя не существует')
    async def get_by_username(self, username: str) -> User | None:
        """Получить пользователя по имени"""
        return await self.UserBase.find_one_by(username=username)

    @rc(exc='user', error_message='Ошибка при создании пользователя')
    async def create_user(self, data: dict) -> User | bool:
        """Создать пользователя"""
        return await self.UserBase.create(data)
    
    @rc(exc='user')
    async def delete_user_in_base(self, user_id: int) -> bool:
        """Удалить пользователя"""
        return await self.UserBase.delete_by_id(user_id)

   
    async def create_token(self, data: dict, token_model: Type[PublicBase]) -> PublicBase | bool:
        """Создать токен"""
        token_repo = BaseRepository(self.session, token_model)
        return await token_repo.create(data)

    async def check_token_info_access_token(self, token: str) -> AccessToken | None:
        """Получить access токен"""
        return await self.AccessTokenBase.find_one_by(access_token=token)

    async def update_token(self, token: str, token_model: Type[PublicBase]) -> bool:
        """Обновить токен"""
        token_obj = await self.check_token_info_access_token(token)
        if not token_obj:
            return False
        token_repo = BaseRepository(self.session, token_model)
        result = await token_repo.update_by_id(token_obj.id, {'access_token': token})
        return result is not None

    async def delete_token_info_access_token(self, token: AccessToken) -> bool:
        """Удалить токен"""
        return await self.AccessTokenBase.delete_by_id(token.id) is not None
    
    @rc(exc='user')
    async def get_user_by_access_token(self, token: str) -> User | None:
        """Получить пользователя по access токену"""
        result = await self.session.execute(
            select(User)
            .join(AccessToken)
            .where(AccessToken.access_token == token)
        )
        return result.scalar_one_or_none()


    # async def get_access_token_by_id(self, user_id: int, token_model: Type[PublicBase]) -> User | None:
    #     token = self.AccessTokenBase.find_one_by(id=user_id)
    #     return 