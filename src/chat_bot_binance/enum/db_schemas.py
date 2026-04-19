from enum import Enum

class TableSchemas(Enum):
    users = """
    CREATE TABLE IF NOT EXISTS users(
        id              INTEGER PRIMARY KEY AUTOINCREMENT,     -- Внутренний уникальный идентификатор записи
        user_id         INTEGER UNIQUE NOT NULL,               -- ID пользователя в Telegram
        admin           BOOLEAN DEFAULT FALSE,                 -- Флаг администратора бота (доступ к спец. функциям)
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- Дата регистрации пользователя в боте
        updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP    -- Дата последнего обновления данных пользователя
    )
    """
