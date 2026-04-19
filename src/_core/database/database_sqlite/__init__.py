"""Асинхронные утилиты для работы с SQLite.

Обеспечивает CRUD-операции, инициализацию схем и управление подключениями.

Методы database_construct:
- construct_create — вставка записи, поддержка INSERT OR IGNORE
- construct_select — выборка с фильтрацией, опционально row_factory
- construct_update — обновление, поддержка count_mode (инкремент/декремент)
- construct_delete — удаление по условию
- construct_execute — произвольный SQL

Инициализация:
- init_database — создание таблиц, индексов, триггеров из Enum
- ensure_table_exists / ensure_index_exists / ensure_trigger_exists — проверка и создание
"""

from .helper import DATABASE_INFO, init_database, init_base
from .core import database_construct, get_db_sqlite

__all__ = [
    'DATABASE_INFO', 
    'init_database', 
    'init_base', 
    'database_construct', 
    'get_db_sqlite']