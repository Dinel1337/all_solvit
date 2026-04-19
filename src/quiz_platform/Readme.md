# Quiz Platform — платформа для квизов `**РАСШИРЕННЫЙ**`
### источник - https://solvit.space/projects/quiz_platform#/

Сервис для создания и прохождения квизов: управление квизами, вопросами, вариантами ответов, публикация, прохождение с сохранением результатов.

Проект построен на **FastAPI** и использует общую библиотеку `_core`, которая предоставляет:
- Унифицированную работу с БД (DatabaseManager, BaseRepository)
- JWT-аутентификацию (токен в cookie, token_dispatch)
- Глобальный обработчик ошибок
- Единый формат ответов (API_response, construct_meta)
- Базовые модели пользователя и CRUD
- Логирование с цветным выводом (LoggerService)
- RaiseControl — декоратор для автоматической генерации 404

## Конфигурация

### Файл config.py:

```python
# DATABASE_NAME = 'quiz_platform'          # Имя Схемы (убрано)
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Префиксы и теги для роутеров
QUIZZES_PREFIX = '/quizzes'
```
## Структура проекта
```plaintext
quiz_platform/
├── main.py                    # Lifespan, инициализация БД, создание приложения
├── config.py                  # Конфигурация
├── api/                       # Эндпоинты
│   ├── dependencies.py        # Зависимости (бд, токены, проверка владельца)
│   ├── quizzes/               # /quizzes (CRUD, публикация, выдача)
│   └── attempts/              # /attempts (прохождение, результаты)
├── local_core/                # Бизнес-логика
│   ├── models/                # SQLAlchemy модели (Quiz, Question, Option, Attempt)
│   ├── schemas/               # Pydantic схемы (CreateQuiz, QuizResponse, SubmitAttempt)
│   ├── repository/            # QuizRepository, AttemptRepository
│   ├── service/               # QuizService — общий сервис
│   └── exceptions/            # QuizNotFoundError, AttemptNotFoundError
└── app.db                     # Файл SQLite (создаётся автоматически)
```

## API Endpoints

### Квизы (`/quizzes`)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/quizzes/` | Создание квиза |
| GET | `/quizzes/` | Список опубликованных квизов (с пагинацией и поиском) |
| GET | `/quizzes/{id}` | Получение квиза по ID |
| PUT | `/quizzes/{id}/publish` | Публикация/снятие с публикации |

### Попытки (`/attempts`)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/quizzes/{id}/attempts` | Начать прохождение квиза |
| POST | `/attempts/{id}/submit` | Отправить ответы и завершить попытку |
| GET | `/attempts/{id}` | Получить результат попытки |

## Модели данных

### Квиз
- `id`, `name`, `description`, `status` (draft/published), `author_id`
- Вопросы: `text`, `points`, `order`
- Опции: `text`, `is_correct`

### Попытка
- `id`, `quiz_id`, `user_id`, `score`, `completed_at`
- Ответы пользователя

## Технические детали

- Авторизация через JWT (cookie/заголовок `Authorization`)
- Права доступа: только владелец может редактировать квиз
- Публиковать может только автор
- В списке `/quizzes/` отображаются только опубликованные квизы

## Используемые компоненты `_core`

- `DatabaseManager` — работа с БД (схема `quiz_platform`)
- `RaiseControl` — обработка 404
- `BaseRepository` — generic CRUD
- `ResponseData` — Swagger-документация
- `StripStringsModel` — авто-очистка строк