from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from ..._core import database_construct
from ..config import path

router = Router()
text = (
    'Вы подписались на мониторинг BTC\n\n'
    'Для остановки мониторинга нажмите /stop'
)

@router.message(CommandStart())
async def start(message:Message, db = database_construct(path)):
    id = message.chat.id
    await db.construct_create(
        {"user_id": id}, ignore_conflict=True
    )
    await message.answer(text)

@router.message(Command('stop'))
async def start(message:Message, db = database_construct(path)):
    id = message.chat.id
    await db.construct_delete(where='user_id = ?', params=(id, ))
    await message.answer('Отписался')