from datetime import datetime, date, timedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, Literal, List
from pydantic import BaseModel

from ..models import Category, MuscleGroup, Workout, WorkoutExercise
from ..repository import ExerciseRepository
from ..repository.workouts_repository import WorkoutRepository, WorkoutExerciseRepository
from ..schemas import *
from ..exceptions.workoute import WorkoutNotFoundError
from src._core.database import get_db

from src._core import StringNormalizer
from src._core.exceptions import AppException, NotFoundError
from src._core.services import LoggerService

_ModelBase = Literal['muscle', 'category']

async def get_exercise_service(
    db: AsyncSession = Depends(get_db)
):
    return ExerciseService(ExerciseRepository(db), WorkoutRepository(db), WorkoutExerciseRepository(db))


class ExerciseService(LoggerService):
    muscle_id_hash: Dict[str, int] = {}
    category_id_hash: Dict[str, int] = {}

    def __init__(
        self,
        repository: ExerciseRepository,
        workout_repository: WorkoutRepository = None,
        workout_exercise_repository: WorkoutExerciseRepository = None
    ) -> None:
        self.repository: ExerciseRepository = repository
        self.workout_repo: WorkoutRepository = workout_repository
        self.workout_exercise_repo: WorkoutExerciseRepository = workout_exercise_repository
        super().__init__()
    def __get_hash(
        self,
        muscle: str,
        category: str,
    ) -> tuple[Optional[int], Optional[int]]:
        self.logger.debug(f"Кэш категорий: {self.category_id_hash}")
        self.logger.debug(f"Кэш мышц: {self.muscle_id_hash}")
        muscle_id: Optional[int] = self.muscle_id_hash.get(muscle.lower(), None) if muscle else None
        category_id: Optional[int] = self.category_id_hash.get(category.lower(), None) if category else None
        
        return muscle_id, category_id

    @classmethod
    def __update_hash(
        cls,
        data: CategoryInDatabase | MuscleInDatabase | Category | MuscleGroup,
        model_type: _ModelBase
    ):
        """Обновляет кэш ID из Pydantic или ORM объекта"""
        if isinstance(data, BaseModel):
            name = data.name
            id_value = data.id
        else:
            name = data.name
            id_value = data.id
        
        if model_type == 'category':
            cls.category_id_hash[name.lower()] = id_value
        else:
            cls.muscle_id_hash[name.lower()] = id_value
    
    async def get_hash_database(self):
        """Загружает кэш ID из базы данных при старте приложения"""
        muscles: List[MuscleGroup] = await self.get_recorg_by_service(model_type='muscle')
        categories: List[Category] = await self.get_recorg_by_service(model_type='category')
        self.__class__.muscle_id_hash = {m.name.lower(): m.id for m in muscles}
        self.__class__.category_id_hash = {c.name.lower(): c.id for c in categories}
        self.logger.info(f"Загружен кэш: {len(muscles)} групп мышц и {len(categories)} категорий")
    
    async def create_exercise(
        self,
        data: CreateExercise,
    ) -> ExerciseInDatabase:
        """Создаёт новое упражнение, проверяя существование категории и группы мышц через кэш"""
        data = StringNormalizer.model(data)
        
        muscle_id, category_id = self.__get_hash(
            data.muscle_group,
            data.category,
        )
        
        
        if muscle_id is None or category_id is None:
            self.logger.warning(f"Не найдены категория '{data.category}' или группа мышц '{data.muscle_group}'")
            raise NotFoundError(resource="Exercise",
                search_param=None,
                message="Неравильные данные",
                error_code="EXERCISE_ERROR",
                details=data.__dict__
                )
        check = await self.repository.get_with_name(data.name)
        if check:
            raise AppException(
                status_code=409,
                message=f'{data.name} уже существует',
                details=str(data.name)
            )
        result = await self.repository.create_exercise(
            data.name,
            category_id,
            muscle_id,
            data.description,
        )
        
        self.logger.info(f"Создано упражнение '{result.name}' (категория: {data.category}, группа мышц: {data.muscle_group})")

        return ExerciseResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            category=result.category.name if result.category else None,
            muscle_group=result.muscle_group.name if result.muscle_group else None,
        )

    async def create_record(
        self,
        data: CreateCategory | CreateMuscle,
        model_type: _ModelBase = 'category'
    ):
        """Создаёт категорию или группу мышц с проверкой дубликата через кэш"""
        data = StringNormalizer.model(data)
        
        if model_type == 'category':
            model = Category
            type_name = "категория"
        else:
            model = MuscleGroup
            type_name = "группа мышц"
        
        name = data.name
        m, c = self.__get_hash(
            muscle=name if model_type == 'muscle' else "",
            category=name if model_type == 'category' else ""
        )
        
        if c or m:
            self.logger.warning(f"Попытка создать дубликат {type_name} '{name}'")
            raise AppException(
                status_code=409,
                message=f'{model_type} уже существует',
                details=str(data.name)
            )
        
        result = await self.repository.create_record(
            model=model,
            name=data.name,
            description=data.description
        )
        
        self.__update_hash(result, model_type=model_type)
        self.logger.info(f"Создана {type_name} '{result.name}' с ID {result.id}")
        return result

    async def get_exercise_by_get(
           self,
           name: Optional[str] = None,
           description: Optional[str] = None,
           category: Optional[str] = None,
           muscle_group: Optional[str] = None,
           id: Optional[int] = None
       ) -> List[ExerciseResponse]:
       
       name, description, category, muscle_group = StringNormalizer.strings(
           name, description, category, muscle_group
       )

       results = None
       if id is not None:
           self.logger.debug(f"Поиск упражнения по ID: {id}")
           result = await self.repository.get_with_id(id)
           results = [result] if result else []
       elif name is not None:
           self.logger.debug(f"Поиск упражнений по названию: {name}")
           results = await self.repository.get_with_name(name)
       elif description is not None:
           self.logger.debug(f"Поиск упражнений по описанию: {description[:50]}...")
           results = await self.repository.get_with_description_pattern(description)
       elif category is not None:
           muscle_id, category_id = self.__get_hash("", category)
           if category_id is None:
               self.logger.warning(f"Категория '{category}' не найдена")
               return []
           results = await self.repository.get_with_category_id(category_id)
       elif muscle_group is not None:
           muscle_id, category_id = self.__get_hash(muscle_group, "")
           if muscle_id is None:
               self.logger.warning(f"Группа мышц '{muscle_group}' не найдена")
               return []
           results = await self.repository.get_with_muscle_group_id(muscle_id)
       else:
           self.logger.debug("Получение всех упражнений")
           results = await self.repository.get_all_exercise()

       self.logger.info(f"Найдено {len(results or [])} упражнений")
       
       return [
           ExerciseResponse(
               id=r.id,
               name=r.name,
               description=r.description,
               category=r.category.name if r.category else None,
               muscle_group=r.muscle_group.name if r.muscle_group else None,
           )
           for r in (results or [])
       ]
    
    async def get_recorg_by_service(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        model_type: _ModelBase = 'category'
    ):
        """Получает список категорий или групп мышц из БД с фильтрацией"""
        if model_type == 'category':
            model = Category
            type_name = "категорий"
        else:
            model = MuscleGroup
            type_name = "групп мышц"
        
        name, description = StringNormalizer.strings(name, description)
        
        if name:
            self.logger.debug(f"Поиск {type_name} по названию: {name}")
            result = await self.repository.get_with_name(name, model)
        elif description:
            self.logger.debug(f"Поиск {type_name} по описанию: {description[:50]}...")
            result = await self.repository.get_with_description_pattern(description, model)
        else:
            self.logger.debug(f"Получение всех {type_name}")
            result = await self.repository.get_all_exercise(model)
        
        self.logger.info(f"Найдено {len(result or [])} {type_name}")
        return result



    # ==================== WORKOUT ====================

    async def create_workout(
            self,
            name: str,
            user_id: int,
            exercises_data: List[Dict[str, Any]],
            description: str = None,
            completed_at: datetime = None
        ) -> Workout:
        """Создать тренировку"""

        enriched_exercises = []
        for idx, ex_data in enumerate(exercises_data):
            exercise_name = ex_data.pop('exercise_name')

            exercise = await self.repository.get_with_name(exercise_name)
            if not exercise:
                raise NotFoundError(
                    resource="Exercise",
                    search_param=exercise_name,
                    message=f"Упражнение '{exercise_name}' не найдено"
                )

            enriched_exercises.append({
                "exercise_id": exercise[0].id if isinstance(exercise, list) else exercise.id,
                "order": idx + 1,
                **ex_data
            })

        workout = await self.workout_repo.create_workout(
            name=name,
            user_id=user_id,
            exercises_data=enriched_exercises,
            description=description,
            completed_at=completed_at
        )
        return workout

    async def get_workout_by_id(self, workout_id: int) -> Workout:
        """Получить тренировку по ID"""
        workout = await self.workout_repo.get_with_id(workout_id)
        if not workout:
            self.logger.warning(f"Тренировка с ID {workout_id} не найдена")
            raise WorkoutNotFoundError(workout_id)
        self.logger.debug(f"Найдена тренировка: {workout.name} (ID: {workout_id})")
        return workout

    async def get_user_workouts(
        self,
        user_id: int,
        limit: int = None
    ) -> List[Workout]:
        """Получить все тренировки пользователя"""
        workouts = await self.workout_repo.get_by_user_id(user_id, limit)
        self.logger.info(f"Найдено {len(workouts)} тренировок у пользователя {user_id}")
        return workouts

    async def get_workouts_by_date_range(
        self,
        user_id: int,
        start_date: date,
        end_date: date
    ) -> List[Workout]:
        """Получить тренировки за период"""
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        workouts = await self.workout_repo.get_by_date_range(
            user_id, start_datetime, end_datetime
        )
        self.logger.info(f"Найдено {len(workouts)} тренировок у пользователя {user_id} за период {start_date} - {end_date}")
        return workouts

    async def get_last_workout(self, user_id: int) -> Optional[Workout]:
        """Получить последнюю тренировку пользователя"""
        workout = await self.workout_repo.get_last_workout(user_id)
        if workout:
            self.logger.debug(f"Последняя тренировка пользователя {user_id}: {workout.name}")
        else:
            self.logger.debug(f"У пользователя {user_id} нет тренировок")
        return workout

    async def update_workout(
        self,
        workout_id: int,
        name: str = None,
        description: str = None,
        completed_at: datetime = None
    ) -> Workout:
        """Обновить тренировки"""
        await self.get_workout_by_id(workout_id)
        
        workout = await self.workout_repo.update_workout(
            workout_id=workout_id,
            name=name,
            description=description,
            completed_at=completed_at
        )
        self.logger.info(f"Обновлена тренировка {workout_id}: {name or 'название не изменено'}")
        return workout

    async def delete_workout(self, workout_id: int) -> bool:
        """Удалить тренировку"""
        await self.get_workout_by_id(workout_id)
        
        result = await self.workout_repo.delete_workout(workout_id)
        self.logger.info(f"Удалена тренировка {workout_id}")
        return result

    async def add_exercise_to_workout(
        self,
        workout_id: int,
        exercise_id: int,
        sets: int,
        reps: int,
        weight: float = None,
        order: int = None
    ) -> WorkoutExercise:
        """Добавить упражнение в тренировку"""
        await self.get_workout_by_id(workout_id)
        
        exercise = await self.workout_exercise_repo.add_exercise_to_workout(
            workout_id=workout_id,
            exercise_id=exercise_id,
            sets=sets,
            reps=reps,
            weight=weight,
            order=order
        )
        self.logger.info(f"Добавлено упражнение {exercise_id} в тренировку {workout_id} ({sets}x{reps}, вес: {weight}кг)")
        return exercise

    async def update_exercise_in_workout(
        self,
        workout_exercise_id: int,
        sets: int = None,
        reps: int = None,
        weight: float = None,
        order: int = None
    ) -> WorkoutExercise:
        """Обновить параметры упражнения в тренировке"""
        result = await self.workout_exercise_repo.update_exercise_in_workout(
            workout_exercise_id=workout_exercise_id,
            sets=sets,
            reps=reps,
            weight=weight,
            order=order
        )
        self.logger.info(f"Обновлено упражнение {workout_exercise_id} в тренировке")
        return result

    async def remove_exercise_from_workout(
        self,
        workout_exercise_id: int
    ) -> bool:
        """Удалить упражнение из тренировки"""
        result = await self.workout_exercise_repo.delete_exercise_from_workout(
            workout_exercise_id
        )
        self.logger.info(f"Удалено упражнение {workout_exercise_id} из тренировки")
        return result

    async def get_workout_exercises(
        self,
        workout_id: int
    ) -> List[WorkoutExercise]:
        """Получить все упражнения в тренировке"""
        await self.get_workout_by_id(workout_id)
        exercises = await self.workout_exercise_repo.get_by_workout_id(workout_id)
        self.logger.debug(f"В тренировке {workout_id} найдено {len(exercises)} упражнений")
        return exercises

    async def get_workout_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику по тренировкам пользователя"""
        stats = await self.workout_repo.get_workout_stats(user_id)
        self.logger.info(f"Получена статистика для пользователя {user_id}: {stats['total_workouts']} тренировок")
        return stats

    async def get_weekly_summary(self, user_id: int) -> Dict[str, Any]:
        """Получить недельную сводку тренировок"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        workouts = await self.workout_repo.get_by_date_range(
            user_id, start_date, end_date
        )
        
        total_exercises = sum(len(w.exercises) for w in workouts)
        total_volume = sum(
            sum(we.weight * we.reps * we.sets for we in w.exercises if we.weight)
            for w in workouts
        )
        
        summary = {
            'period': f"{start_date.date()} - {end_date.date()}",
            'total_workouts': len(workouts),
            'total_exercises': total_exercises,
            'total_volume_kg': round(total_volume, 2),
            'average_workout_length': round(total_exercises / len(workouts), 1) if workouts else 0
        }
        
        self.logger.info(f"Недельная сводка для пользователя {user_id}: {summary['total_workouts']} тренировок, {summary['total_volume_kg']}кг")
        return summary