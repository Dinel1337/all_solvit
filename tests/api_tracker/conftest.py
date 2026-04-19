"""Фикстуры для E2E тестов API Tracker.

Предоставляет:
- app, api_tracker_client — тестовое приложение и HTTP клиент.
- api_tracker_setup — клиент с авторизацией (регистрация + логин).
- add_hash, add_exercise — базовые данные для категорий/упражнений.
- exercise_setup — создаёт 3 категории и 3 группы мышц.
- workout_setup — создаёт 5 упражнений с разными категориями/мышцами.
- final — создаёт 3 тренировки с упражнениями (возвращает клиент и список).

Все фикстуры используют транзакционный откат БД, кэш ExerciseService сбрасывается.
"""

import pytest_asyncio
import pytest
import asyncio


from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src.api_tracker.local_core.service import ExerciseService
from src.api_tracker.app import create_app
from src._core.database.database_alchemy.session import get_db

        
@pytest_asyncio.fixture
def app():
    return create_app(lifespan_enabled=False)

@pytest_asyncio.fixture
async def api_tracker_client(app: FastAPI, db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
    await asyncio.sleep(0.01)
@pytest.fixture(autouse=True)
def clear_exercise_cache():
    """Сбрасывает кэш ExerciseService перед каждым тестом"""
    # Фикс Flaky tests
    
    ExerciseService.muscle_id_hash.clear()
    ExerciseService.category_id_hash.clear()
    yield

@pytest.fixture
def add_hash():
    """Инициализация категории, эта категория сохраниться в виде КЭШИРОВАННОГО *id*"""
    return{
          "description": "Имеет весик",
          "name": "Силовая"
        }

@pytest.fixture
def add_exercise():
    """ Самому себе напомню что поля **muscle_group** и **category** заведомо хешированные и их нужно *отдельно создавать*"""
    return{
      "category": "Силовая", # <--- ТОЕСТЬ, вот это поле нужно инициализировать (фикстура add_hash)
      "description": "Сгибание бла бла бла бла",
      "muscle_group": "Грудь", # <--- Аналогично category, необходимо инициализировать
      "name": "Жим лежа" 
    }

@pytest_asyncio.fixture
async def api_tracker_setup(api_tracker_client, test_reg, test_login):
    await api_tracker_client.post("/auth/register", json=test_reg)
    await api_tracker_client.post("/auth/login", json=test_login)
    return api_tracker_client

@pytest_asyncio.fixture
async def exercise_setup(api_tracker_setup, add_hash):
    """Создаёт 3 категории и 3 группы мышц."""
    categories = ["Силовая", "Кардио", "Растяжка"]
    muscles = ["Грудь", "Ноги", "Спина"]
    
    for name in categories:
        payload = {**add_hash, "name": name}
        await api_tracker_setup.post("/exercises/category/", json=payload)
    
    for name in muscles:
        payload = {**add_hash, "name": name}
        await api_tracker_setup.post("/exercises/muscle/", json=payload)
    
    return api_tracker_setup

@pytest_asyncio.fixture
async def workout_setup(exercise_setup, add_exercise):
    """Создаёт 5 упражнений с разными категориями и группами мышц."""
    
    exercises = [
        {**add_exercise, "name": "Жим лежа", "category": "Силовая", "muscle_group": "Грудь"},
        {**add_exercise, "name": "Присед", "category": "Силовая", "muscle_group": "Ноги"},
        {**add_exercise, "name": "Бег", "category": "Кардио", "muscle_group": "Ноги"},
        {**add_exercise, "name": "Тяга", "category": "Силовая", "muscle_group": "Спина"},
        {**add_exercise, "name": "Растяжка спины", "category": "Растяжка", "muscle_group": "Спина"},
    ]
    
    for ex in exercises:
        r = await exercise_setup.post("/exercises/", json=ex)
        assert r.status_code in [200, 201]
    return exercise_setup

@pytest_asyncio.fixture
async def final(workout_setup):
    """Создаёт 3 уникальные тренировки с упражнениями."""
    
    workouts = [
        {
            "name": "Тренировка груди",
            "description": "Интенсивная тренировка на массу",
            "completed_at": None,
            "exercises": [
                {"exercise_name": "Жим лежа", "sets": 3, "reps": 10, "weight": 50.5}
            ]
        },
        {
            "name": "День ног",
            "description": "Тяжелая тренировка ног",
            "completed_at": None,
            "exercises": [
                {"exercise_name": "Присед", "sets": 4, "reps": 8, "weight": 80.0},
                {"exercise_name": "Бег", "sets": 1, "reps": 1, "weight": None}
            ]
        },
        {
            "name": "Спина и растяжка",
            "description": "Силовая + восстановление",
            "completed_at": "2026-04-03T15:11:24.257Z",
            "exercises": [
                {"exercise_name": "Тяга", "sets": 3, "reps": 12, "weight": 60.0},
                {"exercise_name": "Растяжка спины", "sets": 2, "reps": 15, "weight": None}
            ]
        }
    ]
    
    created_workouts = []
    for w in workouts:
        r = await workout_setup.post("/workouts/", json=w)
        assert r.status_code in [200, 201]
        data = r.json()["data"]
        created_workouts.append(data)
    
    return workout_setup, created_workouts