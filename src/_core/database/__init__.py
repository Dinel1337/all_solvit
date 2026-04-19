"""Базы данных.

Предоставляет:
- SQLAlchemy асинхронный движок (DatabaseManager, get_db, init_db)
- Базовые модели со схемами (PublicBase, ApiTrackerBase, QuizPlatformBase)
- SQLite утилиты (database_construct, инициализация, подключения)

Поддерживаемые БД:
- PostgreSQL (asyncpg)
- SQLite (aiosqlite)
"""

from .database_alchemy import *
from .database_sqlite import *