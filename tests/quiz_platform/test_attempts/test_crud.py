import pytest

@pytest.mark.asyncio
async def test_attempt_full_flow(quiz_platform_setup, add_quiz):
    """E2E тест полного цикла прохождения викторины.

    Покрывает:
    - POST /quizzes/{quiz_id}/attempts — создание попытки (201).
    - PUT /attempts/{attempt_id}/answers — сохранение ответов (200).
    - POST /attempts/{attempt_id}/finish — завершение попытки (200).
    - GET /attempts/{attempt_id}/result — получение результата (200).

    Проверяет:
    - Невозможность повторного завершения (400).
    - Корректность подсчёта баллов.
    - Структуру ответов на всех этапах.
    """
    client = quiz_platform_setup

    quiz_data = {**add_quiz, "status": "published"}
    r = await client.post('/quizzes/', json=quiz_data)
    assert r.status_code == 201, "[POST] Викторина создана"
    quiz = r.json()["data"]
    quiz_id = quiz["id"]

    r = await client.post(f'/quizzes/{quiz_id}/attempts')
    assert r.status_code == 201, "[POST] Попытка создана"
    attempt = r.json()["data"]
    attempt_id = attempt["attempt_id"]

    answers_payload = {"answers": []}
    expected_score = 0
    for q in quiz["questions"]:
        correct_option = next(opt for opt in q["options"] if opt["is_correct"])
        answers_payload["answers"].append({
            "question_id": q["id"],
            "selected_option_id": correct_option["id"]
        })
        expected_score += q["points"]

    r = await client.put(f'/attempts/{attempt_id}/answers', json=answers_payload)
    assert r.status_code == 200, "[PUT] Ответы сохранены"
    saved = r.json()["data"]
    assert saved["saved_count"] == len(answers_payload["answers"])

    r = await client.post(f'/attempts/{attempt_id}/finish')
    assert r.status_code == 200, "[POST] Попытка завершена"
    finish_data = r.json()["data"]
    assert finish_data["score"] == expected_score

    r = await client.post(f'/attempts/{attempt_id}/finish')
    assert r.status_code == 400, "[POST] Повторное завершение → 400"

    r = await client.get(f'/attempts/{attempt_id}/result')
    assert r.status_code == 200, "[GET] Результат получен"
    result = r.json()["data"]
    assert result["attempt_id"] == attempt_id
    assert result["quiz_id"] == quiz_id
    assert result["total_score"] == expected_score
    assert result["max_possible_score"] == expected_score
    assert result["finished_at"] is not None
    assert len(result["answers"]) == len(quiz["questions"])

    for ans in result["answers"]:
        assert ans["is_correct"] is True
        assert ans["earned_points"] > 0

    draft_quiz = {**add_quiz, "status": "draft"}
    r = await client.post('/quizzes/', json=draft_quiz)
    draft_id = r.json()["data"]["id"]
    r = await client.post(f'/quizzes/{draft_id}/attempts')
    assert r.status_code == 400, "[POST] Черновик → 400"

    r = await client.post('/quizzes/999999/attempts')
    assert r.status_code == 404, "[POST] Несуществующий квиз → 404"

    r = await client.put('/attempts/abc/answers', json=answers_payload)
    assert r.status_code == 422, "[PUT] Невалидный attempt_id → 422"