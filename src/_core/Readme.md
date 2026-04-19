# core — общая архитектурная база (DDD shared kernel)

Используется всеми проектами.

Обеспечивает единообразие:
- Работу с БД
- Аутентификацию
- Обработку ошибок
- Формирование ответов
- Переиспользуемые утилиты

## Сложные/обобщённые инструменты

### 1. RaiseControl — фабрика декораторов для 404

**Проблема:** в каждом методе репозитория писать `if not result: raise NotFoundError`

**Решение:** декоратор, который бросает нужную ошибку автоматически, c динамическими ответами

```python
# Настройка маппинга
rc = RaiseControl(
    error_map={"exercise": ExerciseNotFoundError} <---- Маппинг,
    model_error_map={Exercise: ExerciseNotFoundError} <---- динамическое обнаружение ошибки по модели
)

# Использование
@rc.exercise("exercise") <---- #даем понять что бы обрабатывалось ExerciseNotFoundError
async def get_exercise(id: int) -> Exercise | None:
    return await session.get(Exercise, id)
```


### 2. ResponseData — фабрика Swagger-ответов

**Проблема**: повторять `responses={...}` в каждом эндпоинте

**Решение**: централизованное описание с возможностью **динамического** добавления полей

```python
@router.get('/me', responses={
    200: ResponseData.status_200(UserInDB, example={...}),
    401: ResponseData.status_401(ErrorResponse)
})
```


### 3. DatabaseManager — мульти-БД менеджер

**Проблема**: 9 проектов с разными БД

**Решение**: единый менеджер, создающий engine под каждую БД по имени

```python
# Инициализация для проекта api_tracker
await DatabaseManager.init_db("api_tracker")

# Получение сессии
async for session in get_db("api_tracker"):
    ...
```

### 4. BaseRepository — generic CRUD

**Проблема**: повторять CRUD для каждой модели

**Решение**: generic-класс с базовыми методами

```python
class Repository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(session, User)
    # добавляешь только специфичные методы
```

## Общие инфраструктурные компоненты

**Middleware:**
- Логирование запросов
- CORS
- Request ID tracking

**Token Dispatch** — единый диспетчер для разных типов токенов (access/refresh/verify)

**JWT обработка** — унифицированное создание и валидация JWT с поддержкой разных алгоритмов

**Общий обработчик ошибок** — глобальный exception handler с кастомными HTTPException для доменных ошибок

**Общая модель User** — базовая модель с полями: id, email/username, hashed_password, is_active, created_at, updated_at

**Meta & Response** — единая функция для обёртки ответов

**LoggerService**— базовый класс с цветным логгером (INFO при DEBUG, иначе ERROR)

**Общие схемы валидации**

Используются во всех проектах (_core, api_tracker, quiz_platform, chat_bot_binance).

Обеспечивают единообразие:
- Валидация email (email_validator)
- Валидация пароля (длина 6-32 символа)
- Валидация username (буквы/цифры/_, 3-50 символов, без зарезервированных имён)
- Нормализация строк (strip, lower) через StringNormalizer

### Pydantic модели с наследованием от StripStringsModel

**StripStringsModel** — автоматически убирает пробелы у всех строковых полей наследуемых классов.

```python
# ❌ Без StripStringsModel — нужно ручное поле
from pydantic import BaseModel, field_validator

class QueryParams(BaseModel):
    name: str = Field(...)
    
    @field_validator('name')
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip() if v else v

# ✔️ С StripStringsModel — автоматически
from src._core.schemas import StripStringsModel

class QueryParams(StripStringsModel):
    name: str = Field(...)
    # Пробелы у name обрезаются автоматически

Базовые схемы:
- UserBase — email, username
- UserCreate — + password с валидацией
- UserInDB — + id, status_operation
- UserLogin — username + password
- ErrorResponse — error, message, details