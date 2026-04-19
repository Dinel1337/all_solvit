# кол-во assert = 97
"""E2E тесты POST /exercises/ и GET /exercises/.

Покрывает:
- Создание упражнения: валидация name (422/201), проверка дубликатов (409)
- Создание с несуществующими category и muscle_group (404)
- GET /exercises/: поиск по name (частичное совпадение, 200/404)
- Валидация name в query: спецсимволы, пробелы, инъекции (422)
- GET /exercises/: фильтрация по category и muscle_group (200/404/422)
- Проверка, что пробельные и невалидные значения фильтров дают 422
"""

import pytest
from tests.utils import loop_request, loop_request_get

@pytest.mark.asyncio
async def test_exercise(exercise_setup, add_exercise):
    """POST /exercises/ — создание, валидация полей, дубликаты."""
    test_cases_name = {
        '@@zalupa': 422,
        '123zalupa': 422,
        '__': 422,
        '': 422,
        " 22 2 2 ": 422,
        "Жим лежа": 201,
        "Присед": 201,
    }

    test_group = {
        'error': 404,
        " ": 404,
        "  .  ": 404,
        'Сореновновательная': 404
    }
    
    await loop_request(exercise_setup, "/exercises/", add_exercise, test_cases_name, parametr='name', check_dublicate=True)
    await loop_request(exercise_setup, "/exercises/", add_exercise, test_group, parametr='category')
    await loop_request(exercise_setup, "/exercises/", add_exercise, test_group, parametr='muscle_group')


@pytest.mark.asyncio
async def test_exercise_get_name(workout_setup, add_exercise):
    """GET /exercises/ — поиск по name, валидация query-параметра."""
    expected_names = ["Жим лежа", "Присед", "Бег", "Тяга", "Растяжка спины"]
    for name in expected_names:
        r = await workout_setup.get("/exercises/", params={"name": name})
        assert r.status_code == 200
        data = r.json()["data"]
        assert len(data) == 1
        assert data[0]["name"].lower() == name.lower()

    test_cases = {
        "Жим лежа": 200,
        "Растяжка спины": 200,
        "не существует": 404,
        "жим": 200,
        "  Жим лежа  ": 200,
        "": 422,
        "@@bad": 422,
        "123zalupa": 422,
        "__": 422,
        " 22 2 2 ": 422,
        "!@#$%": 422,
        "<script>": 422,
        "'; DROP TABLE": 422,
        "   .   ": 422,
        "𒀱": 422,
        ".": 422,
        "..": 422,
    }
    await loop_request_get(workout_setup, "/exercises/", {}, test_cases, parametr="name")


@pytest.mark.asyncio
async def test_exercise_get_group(workout_setup, add_exercise):
    """GET /exercises/ — фильтрация по category и muscle_group."""
    test_category_cases = {
        "Силовая": 200,
        "Кардио": 200,
        "Растяжка": 200,
        "  Силовая  ": 200,
        "НеСуществует": 404,
        "Йога": 404,
        "Пилатес": 404,
        " ": 422,
        "   .   ": 422,
        "error": 404,
        "@@bad": 422,
        "123": 422,
        "!@#": 422,
    }

    test_muscle_cases = {
        "Грудь": 200,
        "Ноги": 200,
        "Спина": 200,
        "  Грудь  ": 200,
        "Бицепс": 404,
        "Пресс": 404,
        "Ягодицы": 404,
        " ": 422,
        "   .   ": 422,
        "error": 404,
        "@@bad": 422,
        "123": 422,
        "!@#": 422,
    }

    await loop_request_get(workout_setup, "/exercises/", {}, test_category_cases, parametr="category")
    await loop_request_get(workout_setup, "/exercises/", {}, test_muscle_cases, parametr="muscle_group")