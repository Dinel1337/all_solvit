# 30 assert
"""E2E тесты GET/PATCH/DELETE /workouts/{id}.

Покрывает:
- GET /workouts/{id} — успешное получение, невалидные ID (404/422).
- PATCH /workouts/{id} — обновление name, description, completed_at.
- PATCH с невалидными данными: пустой/пробельный name, спецсимволы, короткий/длинный name, невалидная дата.
- DELETE /workouts/{id} — успешное удаление (204), повторный GET → 404.
- DELETE несуществующей тренировки → 404.
- DELETE с невалидными ID → 422.
"""
import pytest
from tests.utils import loop_request

@pytest.mark.asyncio
async def test_get_and_patch_workout(final):
    """Все проверки GET и PATCH /workouts/{id}."""
    client, created = final
    wid = created[0]["id"]

    r = await client.get(f"/workouts/{wid}")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["id"] == wid and data["name"] == created[0]["name"]

    invalid_ids = {"999999": 404, "0": 404, "-1": 404, "abc": 422, "@@": 422, "   ": 422}
    for bad_id, exp in invalid_ids.items():
        r = await client.get(f"/workouts/{bad_id}")
        assert r.status_code == exp, f"GET /workouts/{bad_id} -> {r.status_code}"

    r = await client.patch(f"/workouts/{wid}", json={"name": "Новое название"})
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "Новое название"

    r = await client.patch(f"/workouts/{wid}", json={"description": "Новое описание"})
    assert r.status_code == 200
    assert r.json()["data"]["description"] == "Новое описание"

    new_date = "2026-04-15T10:00:00"
    r = await client.patch(f"/workouts/{wid}", json={"completed_at": new_date})
    assert r.status_code == 200
    assert r.json()["data"]["completed_at"] == new_date

    await loop_request(
        client, f"/workouts/{wid}", {},
        {"": 422, "   ": 422, "@@bad": 422, "123": 422, "ab": 422, "a"*101: 422},
        parametr='name', method='PATCH', check_dublicate=False
    )

    r = await client.patch(f"/workouts/{wid}", json={"completed_at": "invalid"})
    assert r.status_code == 422

    r = await client.patch("/workouts/999999", json={"name": "x"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_delete_workout(final):
    """Все проверки DELETE /workouts/{id}."""
    client, created = final
    wid = created[2]["id"]

    r = await client.delete(f"/workouts/{wid}")
    assert r.status_code == 204
    r = await client.get(f"/workouts/{wid}")
    assert r.status_code == 404

    r = await client.delete("/workouts/999999")
    assert r.status_code == 404

    await loop_request(
        client, "/workouts/", {},
        {"abc": 422, "@@": 422, "-1": 422, "   ": 422},
        parametr='id', method='DELETE', check_dublicate=False
    )