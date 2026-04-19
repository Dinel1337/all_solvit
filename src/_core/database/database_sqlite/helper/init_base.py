import logging
import aiosqlite
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)

async def ensure_table_exists(
    db_connection: aiosqlite.Connection,
    table_name: str,
    table_schema: str,
    check_query: Optional[str] = None
) -> bool:
    """
    Проверяет существование таблицы и создает ее при необходимости
    """
    logger.debug(f"Проверка существования таблицы: {table_name}")
    
    if check_query is None:
        check_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
    
    try:
        async with db_connection.execute(check_query, (table_name,)) as cursor:
            table_exists = await cursor.fetchone() is not None
        
        if not table_exists:
            logger.debug(f"Создание таблицы: {table_name}")
            await db_connection.execute(table_schema)
            await db_connection.commit()
            logger.info(f"Таблица '{table_name}' успешно создана")
            return True
        else:
            logger.debug(f"Таблица '{table_name}' уже существует")
            return False
            
    except aiosqlite.Error as e:
        logger.error(f"Ошибка при проверке/создании таблицы {table_name}: {e}")
        raise

async def ensure_index_exists(
    db_connection: aiosqlite.Connection,
    index_name: str,
    index_schema: str
) -> bool:
    """
    Проверяет существование индекса и создает его при необходимости
    """
    logger.debug(f"Проверка существования индекса: {index_name}")
    
    try:
        check_query = "SELECT name FROM sqlite_master WHERE type='index' AND name=?"
        
        async with db_connection.execute(check_query, (index_name,)) as cursor:
            index_exists = await cursor.fetchone() is not None
        
        if not index_exists:
            logger.debug(f"Создание индекса: {index_name}")
            await db_connection.execute(index_schema)
            await db_connection.commit()
            logger.info(f"Индекс '{index_name}' успешно создан")
            return True
        else:
            logger.debug(f"Индекс '{index_name}' уже существует")
            return False
            
    except aiosqlite.Error as e:
        logger.error(f"Ошибка при проверке/создании индекса {index_name}: {e}")
        raise

async def ensure_trigger_exists(
    db_connection: aiosqlite.Connection,
    trigger_name: str,
    trigger_schema: str
) -> bool:
    """
    Проверяет существование триггера и создает его при необходимости
    """
    logger.debug(f"Проверка существования триггера: {trigger_name}")
    
    try:
        check_query = "SELECT name FROM sqlite_master WHERE type='trigger' AND name=?"
        
        async with db_connection.execute(check_query, (trigger_name,)) as cursor:
            trigger_exists = await cursor.fetchone() is not None
        
        if not trigger_exists:
            logger.debug(f"Создание триггера: {trigger_name}")
            await db_connection.execute(trigger_schema)
            await db_connection.commit()
            logger.info(f"Триггер '{trigger_name}' успешно создан")
            return True
        else:
            logger.debug(f"Триггер '{trigger_name}' уже существует")
            return False
            
    except aiosqlite.Error as e:
        logger.error(f"Ошибка при проверке/создании триггера {trigger_name}: {e}")
        raise

async def init_database(TSC: Enum, db_path: str = 'app.db'):
    """Инициализация базы данных с созданием необходимых таблиц, индексов и триггеров"""
    logger.info(f"Инициализация базы данных: {db_path}")
    
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute('PRAGMA foreign_keys = ON')
            logger.debug("Включены foreign keys")
            
            tables_created = 0
            for table_schema in TSC:
                if await ensure_table_exists(db, table_schema.name, table_schema.value):
                    tables_created += 1
            
            # indexes_created = 0
            # for index in IndexSchemas:
            #     if await ensure_index_exists(db, index.name, index.value):
            #         indexes_created += 1
            
            # triggers_created = 0
            # for trigger in TriggerSchemas:
            #     if await ensure_trigger_exists(db, trigger.name, trigger.value):
            #         triggers_created += 1
            
            # logger.info(
            #     f"Инициализация БД завершена. "
            #     f"Создано: таблиц={tables_created}, индексов={indexes_created}, триггеров={triggers_created}"
            # )
            
            # АДМИНОЧКА
            # try:
            #     await db.execute('INSERT INTO users (username, user_id, admin) VALUES (?, ?, ?)', 
            #                    ('hmstcmbtt', 7508273568, True))
            #     await db.commit()
            #     logger.info("Администратор успешно создан")
            # except aiosqlite.IntegrityError:
            #     await db.rollback()
            #     logger.debug("Администратор уже существует")
            # except Exception as e:
            #     logger.warning(f"Не удалось создать администратора: {e}")
            #     await db.rollback()
                
    except Exception as e:
        logger.error(f"Критическая ошибка при инициализации БД: {e}", exc_info=True)
        raise
    
