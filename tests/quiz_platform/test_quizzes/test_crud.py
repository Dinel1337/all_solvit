import pytest

import pytest

@pytest.mark.asyncio
async def test_quiz_post(quiz_platform_setup, add_quiz):
    """E2E тест POST /quizzes/ + PUT /quizzes/{id}/publish.

    Покрывает:
    - Создание квиза с вопросами и опциями
    - Валидация ответа: статус, name, description, id, author_id
    - Проверка структуры вопросов: text, points, order, id
    - Проверка опций: text, is_correct, id
    - Бизнес-логика: ровно 1 правильный ответ на вопрос
    - Изменение статуса через PUT /publish (draft)
    - Проверка изменения статуса через GET
    """
    r = await quiz_platform_setup.post('/quizzes/', json=add_quiz)
    assert r.status_code == 201, "[POST] Создание квиза — статус 201"

    data = r.json()["data"]
    
    assert data['status'] in ['draft', 'published'], "[POST] Статус draft или published"
    
    for param in ['name', 'description']:
        assert data[param] == add_quiz[param], f"[POST] Поле {param} совпадает"
    
    assert data['id'] > 0, "[POST] ID создан (>0)"
    assert data['author_id'] > 0, "[POST] author_id создан (>0)"
    
    questions = data['questions']
    assert len(questions) == len(add_quiz['questions']), "[POST] Количество вопросов совпадает"
    
    for i, quest in enumerate(questions):
        add_quest = add_quiz['questions'][i]
        assert quest['text'] == add_quest['text'], f"[POST] Вопрос {i}: text совпадает"
        assert quest['points'] == add_quest['points'], f"[POST] Вопрос {i}: points совпадает"
        assert quest['order'] == add_quest['order'], f"[POST] Вопрос {i}: order совпадает"
        assert quest['id'] > 0, f"[POST] Вопрос {i}: ID создан"
        
        options = quest['options']
        assert len(options) == len(add_quest['options']), f"[POST] Вопрос {i}: количество опций совпадает"
        
        correct_count = 0
        for j, opt in enumerate(options):
            add_opt = add_quest['options'][j]
            assert opt['text'] == add_opt['text'], f"[POST] Вопрос {i}, опция {j}: text совпадает"
            assert opt['is_correct'] == add_opt['is_correct'], f"[POST] Вопрос {i}, опция {j}: is_correct совпадает"
            assert opt['id'] > 0, f"[POST] Вопрос {i}, опция {j}: ID создан"
            if opt['is_correct']:
                correct_count += 1
        
        assert correct_count == 1, f"[POST] Вопрос {i}: ровно 1 правильный ответ (получено {correct_count})"

    quiz_id = data['id']
    r = await quiz_platform_setup.put(f'/quizzes/{quiz_id}/publish', json={"publish": "draft"})
    assert r.status_code == 200, "[PUT] /publish — статус 200"
    resp = r.json()
    assert resp["success"] is True, "[PUT] /publish — success=True"
    assert resp["data"] is True, "[PUT] /publish — data=True"

    r_get = await quiz_platform_setup.get(f'/quizzes/{quiz_id}')
    assert r_get.status_code == 200, "[GET] Получение квиза после publish — статус 200"
    assert r_get.json()["data"]["status"] == "draft", "[GET] Статус изменился на draft"