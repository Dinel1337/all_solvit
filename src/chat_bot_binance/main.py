import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv 
from .._core import init_database, database_construct

from .web import check_BTC
from .router import router as all_routers
from .config import path
from .enum import TableSchemas

load_dotenv()
token = os.getenv('TOKEN').strip()
db = database_construct(path)

logger = logging.getLogger(__name__)

bot = Bot(token)
dp = Dispatcher()

async def main():
    try:
        dp.include_router(all_routers)
        await init_database(TableSchemas, path)
        
        await asyncio.gather(
            dp.start_polling(bot),
            check_BTC(bot)
        )
        
    except Exception as e:
        logger.fatal(e, exc_info=True)
    finally:
        logger.info('бот стух :)')


def run():
    """Точка входа для запуска из внешнего модуля."""
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())
