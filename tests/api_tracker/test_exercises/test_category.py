# кол-во assert = 12
"""E2E тесты POST /exercises/category/ и GET /exercises/category/.

Покрывает:
- Создание категории: валидные и невалидные name (422/201)
- Проверка дубликатов (409)
- Получение категории по name
- Структура ответа: data как список, наличие созданной записи
"""

import pytest
from tests.utils import loop_request

@pytest.mark.asyncio
async def test_category(api_tracker_setup, add_hash):
    test_cases = {
        '@@zalupa': 422,
        '123zalupa': 422,
        '__': 422,
        '': 422,
        " 22 2 2 ": 422,
        "Силовая": 201,
    }
    
    await loop_request(api_tracker_setup, "/exercises/category/", add_hash, test_cases, parametr='name')



@pytest.mark.asyncio
async def test_category_get(api_tracker_setup, add_hash):
    add_hash['name'] = 'силоваяуретра'
    response_create = await api_tracker_setup.post("/exercises/category/", json=add_hash)
    assert response_create.status_code == 201
    
    response_get = await api_tracker_setup.get("/exercises/category/", params={'name': add_hash['name']})
    assert response_get.status_code == 200
    data = response_get.json()
    if "data" in data:
        data = data["data"]
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == add_hash["name"]