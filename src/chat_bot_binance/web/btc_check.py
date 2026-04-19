from websockets.asyncio.client import connect
from aiogram import Bot
from ...config import URL_BINANCE
from ..router import broadcast_message

import json
import time

last_sent = 0

async def check_BTC(bot: Bot):
    global last_sent
    async with connect(URL_BINANCE) as websock:
        # from aiohttp import ClientSession, WSMessage   <--- МОЖНО БЫЛО ТАК 
        async for wb in websock:
            now = time.time()
            if now - last_sent >= 5:
                price = json.loads(wb).get('p')
                await broadcast_message(price, bot)
                last_sent = now

