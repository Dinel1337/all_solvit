from contextlib import asynccontextmanager

from pathlib import Path

import aiosqlite

@asynccontextmanager
async def get_db_connection(database : str | Path):
    conn = await aiosqlite.connect(database)
    try:
        yield conn
    finally:
        await conn.close()