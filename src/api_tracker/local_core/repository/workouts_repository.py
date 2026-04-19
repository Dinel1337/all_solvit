from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src._core.repositories.main_repository import BaseRepository
from src._core import RaiseControl
from ..exceptions.workoute import (
    WorkoutNotFoundError, 
    WorkoutExerciseNotFoundError,
    NotFoundError
)
from ..models import Workout, WorkoutExercise, Exercise
from typing import Any, Dict, Optional, List, Literal, Type
from datetime import datetime

_ExcMeta = Literal['workout', 'workout_exercise']
_error_map: Dict[_ExcMeta, Type[NotFoundError]] = {
    "workout": WorkoutNotFoundError,
    "workout_exercise": WorkoutExerciseNotFoundError,
}

_model_error_map = {
    Workout: WorkoutNotFoundError,
    WorkoutExercise: WorkoutExerciseNotFoundError,
}

ExceptionControl = RaiseControl(_error_map, _model_error_map)

class WorkoutRepository(BaseRepository[Workout]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Workout)

    def _get_base_query(self):
        """Базовый запрос с подгрузкой связей (DRY принцип)"""
        return select(Workout).options(
            selectinload(Workout.user),
            selectinload(Workout.exercises).selectinload(WorkoutExercise.exercise)
        )

    @ExceptionControl(exc='workout')
    async def get_with_id(self, id: int) -> Optional[Workout]:
        """Получить тренировку по ID с подгрузкой упражнений"""
        result = await self.session.execute(
            self._get_base_query().where(Workout.id == id)
        )
        return  result.scalar_one_or_none()

    @ExceptionControl(exc='workout')
    async def get_with_name(self, name: str) -> List[Workout]:
        """Найти тренировки по названию (частичное совпадение)"""
        result = await self.session.execute(
            self._get_base_query().where(Workout.name.ilike(f"%{name}%"))
        )
        return result.scalars().all()

    @ExceptionControl(exc='workout')
    async def get_by_user_id(self, user_id: int, limit: int = None) -> List[Workout]:
        """Получить все тренировки пользователя"""
        stmt = self._get_base_query().where(
            Workout.user_id == user_id
        ).order_by(desc(Workout.completed_at))
        
        if limit:
            stmt = stmt.limit(limit)
            
        result = await self.session.execute(stmt)
        return result.scalars().all()

    @ExceptionControl(exc='workout')
    async def get_by_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Workout]:
        """Получить тренировки пользователя за период"""
        result = await self.session.execute(
            self._get_base_query().where(
                Workout.user_id == user_id,
                Workout.completed_at.between(start_date, end_date)
            ).order_by(Workout.completed_at)
        )
        return result.scalars().all()

    @ExceptionControl(exc='workout')
    async def get_last_workout(self, user_id: int) -> Optional[Workout]:
        """Получить последнюю тренировку пользователя"""
        result = await self.session.execute(
            self._get_base_query().where(
                Workout.user_id == user_id
            ).order_by(desc(Workout.completed_at)).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_workouts(self, limit: int = 100) -> List[Workout]:
        """Получить все тренировки (с ограничением)"""
        result = await self.session.execute(
            self._get_base_query().order_by(desc(Workout.completed_at)).limit(limit)
        )
        return result.scalars().all()

    @ExceptionControl(exc='workout')
    async def create_workout(
        self,
        name: str,
        user_id: int,
        exercises_data: List[Dict[str, Any]],
        description: str = None,
        completed_at: datetime = None
    ) -> Workout:
        """Создать тренировку с упражнениями"""
        workout = Workout(
            name=name,
            description=description,
            user_id=user_id,
            completed_at=completed_at or datetime.now()
        )
        self.session.add(workout)
        await self.session.flush()
        
        workout_exercises = [
            WorkoutExercise(
                workout_id=workout.id,
                exercise_id=ex_data['exercise_id'],
                sets=ex_data['sets'],
                reps=ex_data['reps'],
                weight=ex_data.get('weight'),
                order=ex_data.get('order', idx)
            )
            for idx, ex_data in enumerate(exercises_data)
        ]
        self.session.add_all(workout_exercises)
        
        await self.session.commit()
        await self.session.refresh(workout, attribute_names=['exercises', 'user'])
        return workout

    @ExceptionControl(exc='workout')
    async def update_workout(
        self,
        workout_id: int,
        **kwargs
    ) -> Workout:
        """Обновить тренировку (используем базовый update_by_id)"""
        allowed_fields = {'name', 'description', 'completed_at'}
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
        
        if not update_data:
            workout = await self.get_with_id(workout_id)
            return workout
        
        await self.update_by_id(workout_id, update_data)
        
        return await self.get_with_id(workout_id)

    @ExceptionControl(exc='workout')
    async def delete_workout(self, workout_id: int) -> bool:
        """Удалить тренировку (используем базовый delete_by_id)"""
        return await self.delete_by_id(workout_id)

    @ExceptionControl(exc='workout')
    async def get_workout_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику по тренировкам пользователя"""
        total_workouts = await self.session.execute(
            select(func.count(Workout.id)).where(Workout.user_id == user_id)
        )
        
        most_used_exercise = await self.session.execute(
            select(
                Exercise.name,
                func.count(WorkoutExercise.exercise_id).label('count')
            )
            .join(WorkoutExercise)
            .join(Workout)
            .where(Workout.user_id == user_id)
            .group_by(WorkoutExercise.exercise_id, Exercise.name)
            .order_by(desc('count'))
            .limit(1)
        )
        
        total_volume = await self.session.execute(
            select(
                func.sum(WorkoutExercise.weight * WorkoutExercise.reps * WorkoutExercise.sets)
            )
            .join(Workout)
            .where(Workout.user_id == user_id)
        )
        
        return {
            'total_workouts': total_workouts.scalar() or 0,
            'most_used_exercise': most_used_exercise.first(),
            'total_volume_kg': float(total_volume.scalar() or 0)
        }


class WorkoutExerciseRepository(BaseRepository[WorkoutExercise]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, WorkoutExercise)

    def _get_base_query(self):
        """Базовый запрос с подгрузкой связей"""
        return select(WorkoutExercise).options(
            selectinload(WorkoutExercise.workout),
            selectinload(WorkoutExercise.exercise)
        )

    @ExceptionControl(exc='workout_exercise')
    async def get_with_id(self, id: int) -> Optional[WorkoutExercise]:
        """Получить запись упражнения в тренировке по ID"""
        result = await self.session.execute(
            self._get_base_query().where(WorkoutExercise.id == id)
        )
        return result.scalar_one_or_none()

    @ExceptionControl(exc='workout_exercise')
    async def get_by_workout_id(self, workout_id: int) -> List[WorkoutExercise]:
        """Получить все упражнения в тренировке"""
        result = await self.session.execute(
            select(WorkoutExercise)
            .where(WorkoutExercise.workout_id == workout_id)
            .options(selectinload(WorkoutExercise.exercise))
            .order_by(WorkoutExercise.order)
        )
        return result.scalars().all()

    @ExceptionControl(exc='workout_exercise')
    async def update_exercise_in_workout(
        self,
        workout_exercise_id: int,
        **kwargs
    ) -> WorkoutExercise:
        """Обновить параметры упражнения в тренировке"""
        allowed_fields = {'sets', 'reps', 'weight', 'order'}
        update_data = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
        
        if not update_data:
            return await self.get_with_id(workout_exercise_id)
        
        await self.update_by_id(workout_exercise_id, update_data)
        return await self.get_with_id(workout_exercise_id)

    @ExceptionControl(exc='workout_exercise')
    async def delete_exercise_from_workout(self, workout_exercise_id: int) -> bool:
        """Удалить упражнение из тренировки"""
        return await self.delete_by_id(workout_exercise_id)

    @ExceptionControl(exc='workout_exercise')
    async def add_exercise_to_workout(
        self,
        workout_id: int,
        exercise_id: int,
        sets: int,
        reps: int,
        weight: float = None,
        order: int = None
    ) -> WorkoutExercise:
        """Добавить упражнение в существующую тренировку"""
        if order is None:
            max_order = await self.session.execute(
                select(func.max(WorkoutExercise.order))
                .where(WorkoutExercise.workout_id == workout_id)
            )
            order = (max_order.scalar() or 0) + 1
        
        return await self.create({
            'workout_id': workout_id,
            'exercise_id': exercise_id,
            'sets': sets,
            'reps': reps,
            'weight': weight,
            'order': order
        })