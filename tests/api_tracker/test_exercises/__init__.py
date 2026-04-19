# кол-во уникальных assert на модуль 240
"""E2E тесты для модуля Exercises (Упражнения).

Покрытие:
- POST /exercises/ — создание упражнений, валидация полей (name, category, muscle_group), дубликаты.
- GET /exercises/ — поиск по name, фильтрация по category и muscle_group, пагинация.
- POST /exercises/category/ — создание категорий, валидация, дубликаты.
- GET /exercises/category/ — получение категорий по name.
- POST /exercises/muscle/ — создание групп мышц, валидация, дубликаты.
- GET /exercises/muscle/ — получение групп мышц по name.

Все тесты используют фикстуры с транзакционным откатом БД, утилиты loop_request/loop_request_get.
"""