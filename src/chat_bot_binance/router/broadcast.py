from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError
from aiogram.enums import ParseMode
from ..._core import database_construct
from ..config import path
import asyncio


async def broadcast_message(price:int, bot:Bot, db = database_construct(path)):
    all = await db.construct_select('user_id', row_factory=True)
    for user in all:
        user_id = user['user_id']
        try:
            await bot.send_message(user_id, f'BTC -> usdt: <b><strong>{price}</strong></b>', parse_mode=ParseMode.HTML)
        except TelegramNetworkError:
            pass
        finally:
            await asyncio.sleep(0.1)