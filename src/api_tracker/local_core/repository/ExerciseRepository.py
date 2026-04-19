from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src._core.repositories.main_repository import BaseRepository
from src._core.database import PublicBase
from src._core import RaiseControl
from ..exceptions.workoute import ExerciseNotFoundError, CategoryNotFoundError, MuscleGroupNotFoundError, NotFoundError
from ..models import Exercise, MuscleGroup, Category
from typing import Type, Any, Literal, Dict

_ExcMeta = Literal['exercise', 'category', 'muscle_group']
_error_map: Dict[_ExcMeta, Type[NotFoundError]] = {
    "exercise": ExerciseNotFoundError,
    "category": CategoryNotFoundError,
    "muscle_group": MuscleGroupNotFoundError,
}

_model_error_map = {
    Exercise: ExerciseNotFoundError,
    Category: CategoryNotFoundError,
    MuscleGroup: MuscleGroupNotFoundError,
}

rc = RaiseControl(_error_map, _model_error_map)

class ExerciseRepository(BaseRepository[Exercise]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(session, Exercise)

    @rc(exc='exercise')
    async def get_with_id(self, id: int):
        result = await self.session.execute(
            select(Exercise)
            .options(
                selectinload(Exercise.category),
                selectinload(Exercise.muscle_group)
            )
            .where(Exercise.id == id)
        )
        return result.scalar_one_or_none()

    @rc(exc='exercise', model_pos=2)
    async def get_with_name(self, name: str, model: Any = None):
        if model:
            return await BaseRepository(self.session, model).find_scalars_by(name=name)

        stmt = select(Exercise).where(Exercise.name.ilike(f"%{name}%")).options(
            selectinload(Exercise.category),
            selectinload(Exercise.muscle_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @rc(exc='exercise')
    async def get_with_category_id(self, category_id: int):
        stmt = select(Exercise).where(Exercise.category_id == category_id).options(
            selectinload(Exercise.category),
            selectinload(Exercise.muscle_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @rc(exc='exercise')
    async def get_with_muscle_group_id(self, muscle_group_id: int):
        stmt = select(Exercise).where(Exercise.muscle_group_id == muscle_group_id).options(
            selectinload(Exercise.category),
            selectinload(Exercise.muscle_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @rc(search_field='description', model_pos=2)
    async def get_with_description_pattern(self, pattern: str, model: Type[PublicBase] = None):
        if model:
            stmt = select(model).where(model.description.ilike(f'%{pattern}%'))
            result = await self.session.execute(stmt)
            return result.scalars().all()

        stmt = select(Exercise).where(Exercise.description.ilike(f'%{pattern}%')).options(
            selectinload(Exercise.category),
            selectinload(Exercise.muscle_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_all_exercise(self, model: Any = None):
        if model:
            return await BaseRepository(self.session, model).find_scalars_by()

        stmt = select(Exercise).options(
            selectinload(Exercise.category),
            selectinload(Exercise.muscle_group)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @rc(exc='exercise')
    async def create_exercise(
        self,
        name: str,
        category_id: int,
        muscle_group_id: int,
        description: str = None
    ) -> Exercise:
        """Создать упражнение"""
        instance = Exercise(
            name=name,
            description=description,
            category_id=category_id,
            muscle_group_id=muscle_group_id
        )
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance, attribute_names=['category', 'muscle_group'])
        return instance

    @rc(model_pos=1)
    async def create_record(
        self,
        model: Type[PublicBase],
        name: str,
        description: str = None
    ) -> Category | MuscleGroup:
        model_obj = BaseRepository(self.session, model)
        return await model_obj.create({
            'name': name,
            'description': description,
        })  