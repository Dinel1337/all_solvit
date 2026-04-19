"""SQLAlchemy асинхронные модели и менеджер БД.

Компоненты:
- DatabaseManager — управление engine и session maker
- get_db — dependency для получения сессии
- init_db — инициализация схем (create_all)
- PublicBase, ApiTrackerBase, QuizPlatformBase — базовые модели со схемами

Особенности:
- Автоматическое создание схем public, api_tracker, quiz_platform
- В режиме TESTING — новый engine без пула (отключён кеш)
- Поддержка asyncpg и aiosqlite
"""
from .base import ApiTrackerBase, QuizPlatformBase, PublicBase
from .session import get_db, init_db, DatabaseManager

__all__ = ['ApiTrackerBase', 'QuizPlatformBase', 'get_db', 'init_db', 'DatabaseManager', 'PublicBase']