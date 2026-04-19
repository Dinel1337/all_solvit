from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import PublicBase
from typing import Generic, TypeVar, Type, Optional, Any, List
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=PublicBase)

class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model
    
    async def find_one_by(self, **filters) -> Optional[T]:
        """
        Поиск одной записи по фильтрам.
        
        Параметры:
        - **filters: Именованные аргументы для фильтрации (column=value)
        
        Возвращает:
        - Optional[T]: Найденный объект или None
        """
        result = await self.session.execute(
            select(self.model).filter_by(**filters)
        )
        return result.scalar_one_or_none()
    
    async def find_one_by_with_options(self, options: list, **kwargs):
        stmt = select(self.model).filter_by(**kwargs).options(*options)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find_scalar_by(self, column: Any,options: Optional[List] = None, **filters) -> Optional[Any]:
        """Получить одно значение колонки по фильтрам"""
        query = select(column).filter_by(**filters)
        if options:
            query = query.options(*options)
        result = await self.session.execute(query)
        
        return result.scalar_one_or_none()
    
    async def find_scalars_by(self, **filters) -> Optional[Any]:
        result = await self.session.execute(
            select(self.model).filter_by(**filters)
        )
        return result.scalars().all()
    
    async def create(self, data: dict, commit:bool = True) -> T | bool:
        """
        Создание новой записи.
        
        Параметры:
        - data: Словарь с данными для создания записи
        
        Возвращает:
        - T | bool: Созданный объект или False в случае ошибки
        """
        try:
            instance = self.model(**data)
            self.session.add(instance)
            if commit:
                await self.session.commit()
                await self.session.refresh(instance)
            else:
                await self.session.flush()
            return instance
        except Exception as e:
            logger.error(f"Ошибка создания {self.model.__name__}: {e}")
            await self.session.rollback()
            raise
    
    async def delete_by_id(self, record_id: int) -> bool:
        """
        Удаление записи по ID.
        
        Параметры:
        - record_id: ID записи для удаления
        
        Возвращает:
        - bool: True если запись удалена, False если не найдена или ошибка
        """
        try:
            result = await self.session.execute(
                delete(self.model).where(self.model.id == record_id)
            )
            await self.session.commit()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка удаления {self.model.__name__}: {e}")
            await self.session.rollback()
            return False

    async def update_by_id(self, id: int, update_data: dict) -> bool:
        """
        Обновление записи по ID.
        
        Параметры:
        - id: ID записи для обновления
        - update_data: Словарь с данными для обновления
        
        Возвращает:
        - bool: True если запись обновлена, False если не найдена или ошибка
        """
        try:
            
            stmt = update(self.model).where(
                self.model.id == id
            ).values(**update_data)
            
            result = await self.session.execute(stmt)
            await self.session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating {self.model.__name__} with id {id}: {e}")
            return False