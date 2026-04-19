"""E2E тесты POST /workouts/ и GET /workouts/.

Покрывает:
- POST /workouts/ — создание 3 тренировок с упражнениями, валидация name (422/201).
- Негативные кейсы POST: без exercises, пустые exercises, несуществующее упражнение (404).
- GET /workouts/ — получение списка, проверка наличия созданных тренировок.
- GET /workouts/{id} — получение по ID, сравнение структуры.
- GET /workouts/ с невалидными ID: 404/422.
- Пагинация: валидация limit и offset через loop_request_get.
"""

import pytest
from tests.utils import loop_request_get, loop_request

@pytest.mark.asyncio
async def test_create_workout_success(final):
    """Успешное создание тренировки."""
    client, created_workouts = final
    
    assert len(created_workouts) == 3
    assert created_workouts[0]["name"] == "Тренировка груди"
    assert created_workouts[1]["name"] == "День ног"
    assert created_workouts[2]["name"] == "Спина и растяжка"
    
    for w in created_workouts:
        assert "id" in w
        assert "name" in w
        assert "exercises" in w
        assert len(w["exercises"]) > 0


@pytest.mark.asyncio
async def test_create_workout_invalid(final):
    """Невалидные случаи создания тренировки."""
    client, _ = final
    
    base_payload = {
        "description": "Тестовая тренировка",
        "exercises": [{"exercise_name": "Жим лежа", "sets": 3, "reps": 10}]
    }
    
    test_cases_name = {
        # Валидные
        "Тренировка А": 201,
        "Тренировка Б": 201,
        "Ноги": 201,
        "  Спина  ": 201,
        # Невалидные
        "": 422,
        "   ": 422,
        "@@bad": 422,
        "123": 422,
        "!@#": 422,
        "__": 422,
        " 22 2 2 ": 422,
    }
    
    await loop_request(client, "/workouts/", base_payload, test_cases_name, parametr='name', check_dublicate=False)
    
    r = await client.post("/workouts/", json={"name": "Без упражнений"})
    assert r.status_code == 422
    
    r = await client.post("/workouts/", json={"name": "Пустые упражнения", "exercises": []})
    assert r.status_code == 422
    
    r = await client.post("/workouts/", json={"name": "Несуществующее", "exercises": [{"exercise_name": "НеСуществует", "sets": 3, "reps": 10}]})
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_get_workouts(final):
    """Получение списка тренировок и проверка наличия созданных."""
    client, created_workouts = final
    
    r = await client.get("/workouts/")
    assert r.status_code == 200
    data = r.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 3
    
    workout_ids = {w["id"] for w in data}
    for created in created_workouts:
        assert created["id"] in workout_ids


@pytest.mark.asyncio
async def test_get_workout_by_id(final):
    """Получение тренировки по ID."""
    client, created_workouts = final
    
    for workout in created_workouts:
        r = await client.get(f"/workouts/{workout['id']}")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["id"] == workout["id"]
        assert data["name"] == workout["name"]
        assert len(data["exercises"]) == len(workout["exercises"])


@pytest.mark.asyncio
async def test_get_workout_not_found(final):
    """Получение несуществующей тренировки."""
    client, _ = final
    
    test_cases_id = {
        "999999": 404,
        "0": 404,
        "-1": 404,
        "abc": 422,
        "@@": 422,
    }
    
    for id_val, expected in test_cases_id.items():
        r = await client.get(f"/workouts/{id_val}")
        assert r.status_code == expected, f"GET /workouts/{id_val}: ожидался {expected}, получен {r.status_code}"


@pytest.mark.asyncio
async def test_workouts_pagination(final):
    """Пагинация: limit и offset."""
    client, _ = final
    
    test_cases_limit = {
        "1": 200,
        "5": 200,
        "10": 200,
        "100": 200,
        "0": 422,
        "-1": 422,
        "abc": 422,
        "": 422,
    }
    await loop_request_get(client, "/workouts/", {}, test_cases_limit, parametr="limit", skip_data_check=True)
    
    test_cases_offset = {
        "0": 200,
        "1": 200,
        "10": 200,
        "-1": 422,
        "abc": 422,
        "": 422,
    }
    await loop_request_get(client, "/workouts/", {}, test_cases_offset, parametr="offset", skip_data_check=True)
