# кол-во assert = 12
"""E2E тесты POST /exercises/muscle/ и GET /exercises/muscle/.

Покрывает:
- Создание группы мышц: валидные и невалидные name (422/201)
- Проверка дубликатов (409)
- Получение группы мышц по name
- Структура ответа: data как список, наличие созданной записи
"""

import pytest
from tests.utils import loop_request

@pytest.mark.asyncio
async def test_muscle(api_tracker_setup, add_hash):
    """POST /exercises/muscle/ — создание, валидация, дубликаты."""
    test_cases = {
        '@@zalupa': 422,
        '123zalupa': 422,
        '__': 422,
        '': 422,
        " 22 2 2 ": 422,
        "Грудь": 201,
        "СисичКИ": 201,
    }
    
    await loop_request(api_tracker_setup, "/exercises/muscle/", add_hash, test_cases, parametr='name')


@pytest.mark.asyncio
async def test_muscle_get(api_tracker_setup, add_hash):
    """GET /exercises/muscle/ — поиск по name, структура ответа."""
    add_hash['name'] = 'груднаяуретра'
    response_create = await api_tracker_setup.post("/exercises/muscle/", json=add_hash)
    assert response_create.status_code == 201
    
    response_get = await api_tracker_setup.get("/exercises/muscle/", params={'name': add_hash['name']})
    assert response_get.status_code == 200
    data = response_get.json()
    if "data" in data:
        data = data["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == add_hash["name"]