# import os

# script_dir = os.path.dirname(os.path.abspath(__file__))
# path = os.path.join(script_dir, 'app.db')
# # НУЖНО ЧТО БЫ СОЗДАВАТЬ ЛОКАЛЬНЫЕ БД В КАЖДОМ ПРОЕКТЕ

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
DATABASE_NAME = 'api_tracker'

#user config
AUTH_PREFIX = '/auth'
AUTH_TAGS = ['auth']

USERS_PREFIX = '/users'
USERS_TAGS   = ['users']

EXERCISES_PREFIX = '/exercises'
EXERCISES_TAGS = ['exercises']

CATEGORIES_PREFIX = EXERCISES_PREFIX + '/category'
CATEGORIES_TAGS = EXERCISES_TAGS

MUSCLES_PREFIX = EXERCISES_PREFIX + '/muscle'
MUSCLES_TAGS = EXERCISES_TAGS

WORKOUT_PREFIX = '/workouts'
WORKOUT_TAGS = ['workouts']

REPORTS_PREFIX = "/reports"
REPORTS_TAGS = ["reports"]

USER_ROUTER_CREATE = '/create'
USER_ROUTER_DELETE = '/delete'
USER_ROUTER_CHECK = '/check'


OpenAPI_text = """
**Бэкенд для трекера тренировок: регистрация пользователей, список упражнений, планы тренировок, расписание и отчёты.**


**Все запросы к личным тренировкам защищены JWT-токенами.**


Для полноценного тестирования необходимо:

1. **Зарегистрироваться** (через эндпойнт **`/auth/signup`**).


2. **Получить JWT-токен** (через **`/auth/login`**).


3. **Нажать кнопку** **`Authorize`** в правом верхнем углу Swagger UI и вставить токен в формате: **`<your_access_token>`**.



**О проекте:**

Пользователь может регистрироваться, входить в аккаунт, составлять планы тренировок и отслеживать прогресс. Система поддерживает создание, редактирование и удаление тренировок (CRUD), а также формирует отчёты по прошлым занятиям.


**Основные разделы API:**

- **auth** — регистрация, вход, выход

- **users** — профиль пользователя

- **exercises** — справочник упражнений (кардио, силовые, растяжка, по группам мышц)

- **workouts** — создание, редактирование, удаление тренировок (с подходами, повторениями и весом)

- **reports** — отчёты о прогрессе за выбранный период



**Технические детали:**

- Реляционная база данных (SQLite/PostgreSQL)

- REST API

- JWT-аутентификация

- Минимальные тесты для проверки логики



*Проект **расширен** от базовой задачи и приближен к реальному продакшн-бэкенду.*
"""