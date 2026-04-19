# API Tracker — трекер тренировок `**РАСШИРЕННЫЙ**`
### источник - https://solvit.space/projects/workout_tracker#/
Сервис для ведения тренировок: управление упражнениями, категориями, группами мышц, создание тренировок с подходами/повторениями/весами, получение статистики и отчётов.

Проект построен на **FastAPI** и использует общую библиотеку `core`, которая предоставляет:
- Унифицированную работу с БД (DatabaseManager, BaseRepository)
- JWT-аутентификацию (токен в cookie, token_dispatch)
- Глобальный обработчик ошибок
- Единый формат ответов (API_response, construct_meta)
- Базовые модели пользователя и CRUD
- Логирование с цветным выводом (LoggerService)

```bash
poetry run python main.py -n 2
```
Где цифра два это порядковый номер проекта

## Конфигурация
### Файл config.py:

```python
DATABASE_NAME = 'api_tracker'          # Имя БД
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Префиксы и теги для роутеров
AUTH_PREFIX = '/auth'
USERS_PREFIX = '/users'
...
```
## Структура проекта
```plaintext
api_tracker/
├── main.py                    # Lifespan, инициализация БД, создание приложения
├── config.py                  # Конфигурация
├── api/                       # Эндпоинты
│   ├── auth/                  # /auth (login, register, logout)
│   ├── users/                 # /users (profile)
│   ├── exercises/             # /exercises, /exercises/category, /exercises/muscle
│   ├── workout/               # /workout (CRUD тренировок)
│   ├── reports/               # /reports (summary, progress)
│   └── dependencies.py        # Зависимости(бд, токены)
├── local_core/                # Бизнес-логика
│   ├── models/                # SQLAlchemy модели
│   ├── schemas/               # Pydantic схемы
│   ├── repository/            # Репозитории для сервиса
│   ├── service.py             # ExerciseService общий сервис для всего проекта
│   ├── exceptions/            # Кастомные ошибки
│   └── session.py             # get_api_tracker_db
└── app.db                     # Файл SQLAlchemy (создаётся автоматически)
```