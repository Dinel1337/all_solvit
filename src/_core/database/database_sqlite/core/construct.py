import logging
from pathlib import Path
from typing import Any, Optional, Tuple, Literal

_tableStr = Literal['users']
_where = Literal['user_id = ? '] | str
from ..connection import get_db_connection
import aiosqlite

logger = logging.getLogger(__name__)

class database_construct():
    def __init__(self, name_db: str | Path):
        self.database = name_db
        logger.debug(f"Инициализирован database_construct с базой: {name_db}")

    async def construct_create(self, data: dict[str, Any], table: _tableStr = "users", ignore_conflict: bool = False):
        """Вставка данных в таблицу с опцией игнорирования конфликтов"""
        logger.debug(f"CREATE запрос: таблица={table}, данные={data}, ignore_conflict={ignore_conflict}")
        
        try:
            async with get_db_connection(self.database) as db:
                columns = ", ".join(data.keys())
                placeholders = ", ".join(["?"] * len(data))
                values = list(data.values())
                
                if ignore_conflict:
                    query = f'INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})'
                else:
                    query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
                    
                cursor = await db.execute(query, values)
                await db.commit()
                
                last_id = cursor.lastrowid
                logger.debug(f"Успешная вставка в {table}, ID: {last_id}")
                return last_id
                
        except Exception as e:
            logger.error(f"Ошибка в construct_create для таблицы {table}: {e}", exc_info=True)
            raise

    async def construct_select(self, 
                             columns: str = "*", 
                             table: _tableStr = "users", 
                             where: _where = None,
                             params: Optional[Tuple[Any, ...]] = None,
                             row_factory: int = None,
                             one: bool = False):
        """Выборка данных из таблицы"""
        logger.debug(f"SELECT запрос: таблица={table}, columns={columns}, where={where}, params={params}")
        
        try:
            async with get_db_connection(self.database) as db:
                if row_factory:
                    db.row_factory = aiosqlite.Row

                query = f'SELECT {columns} FROM {table}'
                if where:
                    query += f' WHERE {where}'
                
                cursor = await db.execute(query, params or ())
                results = await cursor.fetchone() if one else await cursor.fetchall()
                
                if not results:
                    logger.warning(f"SELECT не вернул данных: таблица={table}, where={where}")
                
                logger.debug(f"SELECT вернул {len(results) if isinstance(results, list) else 1} записей")
                return results
                
        except Exception as e:
            logger.error(f"Ошибка в construct_select для таблицы {table}: {e}", exc_info=True)
            raise

    async def construct_update(self, 
                             data: Optional[dict[str, Any]] = None, 
                             table: _tableStr = "users", 
                             where: Optional[str] = None,
                             params: Optional[Tuple[Any, ...]] = None,
                             count_mode: bool = False,
                             set_count: str = None,
                             value_count: str = None):
        """Обновление данных в таблице"""
        logger.debug(f"UPDATE запрос: таблица={table}, where={where}, count_mode={count_mode}, set_count={set_count}, value_count={value_count}")
        
        try:
            async with get_db_connection(self.database) as db:
                if not count_mode:
                    if not data:
                        logger.warning(f"UPDATE вызван без данных для обновления: таблица={table}")
                        return 0
                    set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
                    values = list(data.values())
                else:
                    if not set_count or value_count is None:
                        logger.warning(f"count_mode требует set_count и value_count: таблица={table}")
                        return 0
                    
                    column_name = set_count.replace('=', '').strip().split()[0] if '=' in set_count else set_count.strip()
                    
                    if value_count.startswith('-'):
                        operator = '-'
                        numeric_value = value_count[1:]
                    else:
                        operator = '+'
                        numeric_value = value_count
                    
                    set_clause = f"{column_name} = {column_name} {operator} ?"
                    values = [numeric_value]
                    
                    logger.debug(f"count_mode: column={column_name}, operator={operator}, value={numeric_value}")
                
                query = f'UPDATE {table} SET {set_clause}'
                if where:
                    query += f' WHERE {where}'
                    values.extend(params or ())
                
                logger.debug(f"Выполняется запрос: {query} с параметрами: {values}")
                
                cursor = await db.execute(query, values)
                await db.commit()
                
                row_count = cursor.rowcount
                if row_count == 0:
                    logger.warning(f"UPDATE не затронул ни одной строки: таблица={table}, where={where}")
                else:
                    logger.debug(f"UPDATE затронул {row_count} строк в таблице {table}")
                
                return row_count
                
        except Exception as e:
            logger.error(f"Ошибка в construct_update для таблицы {table}: {e}", exc_info=True)
            raise
        
    async def construct_delete(self, 
                             table: _tableStr = "users", 
                             where: Optional[str] = None,
                             params: Optional[Tuple[Any, ...]] = None):
        """Удаление данных из таблицы"""
        logger.debug(f"DELETE запрос: таблица={table}, where={where}")
        
        try:
            async with get_db_connection(self.database) as db:
                query = f'DELETE FROM {table}'
                if where:
                    query += f' WHERE {where}'
                
                cursor = await db.execute(query, params or ())
                await db.commit()
                
                row_count = cursor.rowcount
                if row_count == 0:
                    logger.warning(f"DELETE не затронул ни одной строки: таблица={table}, where={where}")
                else:
                    logger.debug(f"DELETE удалил {row_count} строк из таблицы {table}")
                
                return row_count
                
        except Exception as e:
            logger.error(f"Ошибка в construct_delete для таблицы {table}: {e}", exc_info=True)
            raise

    async def construct_execute(self, query: str, params: Optional[Tuple[Any, ...]] = None):
        """Выполнение произвольного SQL запроса"""
        logger.debug(f"EXECUTE запрос: {query}, params={params}")
        
        try:
            async with get_db_connection(self.database) as db:
                cursor = await db.execute(query, params or ())
                
                if query.strip().upper().startswith('SELECT'):
                    results = await cursor.fetchall()
                    logger.debug(f"EXECUTE SELECT вернул {len(results)} записей")
                    return results
                else:
                    await db.commit()
                    row_count = cursor.rowcount
                    logger.debug(f"EXECUTE затронул {row_count} строк")
                    return row_count
                    
        except Exception as e:
            logger.error(f"Ошибка в construct_execute для запроса {query}: {e}", exc_info=True)
            raise

async def get_db_sqlite(path = 'app.db'):
    try:
        db = await database_construct(path)
        yield
    except Exception as E:
        repr(E)
    finally:
        if hasattr(db, 'close'):
            await db.close()