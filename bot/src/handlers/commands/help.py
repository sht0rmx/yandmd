from aiogram import types
from aiogram.filters import Command

from handlers import router
from utils.messages import get_data


@router.message(Command("help"))
async def send_help(msg: types.Message):
    await msg.answer(**await get_data(msg, "help"))
