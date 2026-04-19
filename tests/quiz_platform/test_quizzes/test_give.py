import pytest

@pytest.mark.asyncio
async def test_quiz_get_all(quiz_platform_setup, add_quiz):
    """E2E тест GET /quizzes/ и /quizzes/{id}.
    Покрывает:
    - Создание 2 published и 1 draft квизов
    - GET списка: только published, черновик скрыт
    - GET по ID: published и draft доступны владельцу
    - 404 для несуществующего ID
    - 422 для невалидных ID (abc, @@, -1, пробелы)
    - Поиск по name и description (частичное совпадение)
    - Поиск по черновику — пустой список
    - Пагинация: limit, offset
    - Валидация limit (0, -1, 501, abc) и offset (-1, abc)
    """
    
    client = quiz_platform_setup
    
    quiz1 = {**add_quiz, "name": "Python Basics", "description": "Основы Python", "status": "published"}
    quiz2 = {**add_quiz, "name": "JavaScript Pro", "description": "Продвинутый JS", "status": "published"}
    quiz3 = {**add_quiz, "name": "Draft Quiz", "description": "Черновик", "status": "draft"}
    
    created = []
    for i, q in enumerate([quiz1, quiz2, quiz3]):
        r = await client.post('/quizzes/', json=q)
        assert r.status_code == 201, f"[POST] Создание квиза {i+1}"
        created.append(r.json()["data"])
    
    published = [q for q in created if q["status"] == "published"]
    draft = [q for q in created if q["status"] == "draft"]
    
    r = await client.get('/quizzes/')
    assert r.status_code == 200, "[GET] Список квизов — статус"
    data = r.json()["data"]
    assert len(data) == 2, "[GET] Список квизов — только 2 published"
    assert all(q["status"] == "published" for q in data), "[GET] Все в списке — published"
    assert draft[0]["id"] not in [q["id"] for q in data], "[GET] Черновик не попал в список"
    
    for quiz in published:
        r = await client.get(f"/quizzes/{quiz['id']}")
        assert r.status_code == 200, f"[GET/{quiz['id']}] Получение published квиза"
        data = r.json()["data"]
        assert data["id"] == quiz["id"], f"[GET/{quiz['id']}] ID совпадает"
        assert data["name"] == quiz["name"], f"[GET/{quiz['id']}] name совпадает"
        assert data["status"] == "published", f"[GET/{quiz['id']}] status=published"
        assert "questions" in data, f"[GET/{quiz['id']}] Есть поле questions"
    
    r = await client.get(f"/quizzes/{draft[0]['id']}")
    assert r.status_code == 200, f"[GET/{draft[0]['id']}] Черновик доступен владельцу"
    data = r.json()["data"]
    assert data["status"] == "draft", f"[GET/{draft[0]['id']}] status=draft"
    
    r = await client.get("/quizzes/999999999")
    assert r.status_code == 404, "[GET/999999999] Несуществующий ID → 404"
    

    for bad_id in ["abc", "@@", "-1", "   "]:
        r = await client.get(f"/quizzes/{bad_id}")
        assert r.status_code == 422, f"[GET/{bad_id}] Невалидный ID → 422"
    
    r = await client.get('/quizzes/', params={"search": "Python"})
    assert r.status_code == 200, "[GET] Поиск по name 'Python' — статус"
    data = r.json()["data"]
    assert len(data) == 1, "[GET] Поиск по name 'Python' — 1 результат"
    assert data[0]["name"] == "Python Basics", "[GET] Поиск по name 'Python' — имя совпадает"
    
    r = await client.get('/quizzes/', params={"search": "Продвинутый"})
    assert r.status_code == 200, "[GET] Поиск по description 'Продвинутый' — статус"
    data = r.json()["data"]
    assert len(data) == 1, "[GET] Поиск по description 'Продвинутый' — 1 результат"
    assert data[0]["name"] == "JavaScript Pro", "[GET] Поиск по description — имя совпадает"
    
    r = await client.get('/quizzes/', params={"search": "НеСуществует"})
    assert r.status_code == 200, "[GET] Поиск 'НеСуществует' — статус"
    data = r.json()["data"]
    assert len(data) == 0, "[GET] Поиск 'НеСуществует' — пустой список"
    
    r = await client.get('/quizzes/', params={"search": "Draft"})
    assert r.status_code == 200, "[GET] Поиск 'Draft' — статус"
    data = r.json()["data"]
    assert len(data) == 0, "[GET] Поиск 'Draft' — черновик не виден в списке"
    
    r = await client.get('/quizzes/', params={"limit": 1})
    assert r.status_code == 200, "[GET] limit=1 — статус"
    data = r.json()["data"]
    assert len(data) == 1, "[GET] limit=1 — вернул 1 запись"
    
    r = await client.get('/quizzes/', params={"limit": 1, "offset": 1})
    assert r.status_code == 200, "[GET] limit=1, offset=1 — статус"
    data = r.json()["data"]
    assert len(data) == 1, "[GET] limit=1, offset=1 — вернул 1 запись"
    r_first = await client.get('/quizzes/', params={"limit": 1, "offset": 0})
    assert data[0]["id"] != r_first.json()["data"][0]["id"], "[GET] offset=1 — ID отличается от offset=0"
    
    for bad_limit in [0, -1, 501, "abc", ""]:
        r = await client.get('/quizzes/', params={"limit": bad_limit})
        assert r.status_code == 422, f"[GET] limit={bad_limit} → 422"
    
    for bad_offset in [-1, "abc", ""]:
        r = await client.get('/quizzes/', params={"offset": bad_offset})
        assert r.status_code == 422, f"[GET] offset={bad_offset} → 422"