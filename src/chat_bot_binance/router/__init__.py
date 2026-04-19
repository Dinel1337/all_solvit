from aiogram import Router
from .broadcast import broadcast_message
from .binance_router import router as binance

all = [binance]
router = Router()

router.include_routers(binance)