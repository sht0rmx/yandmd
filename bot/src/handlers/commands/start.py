from aiogram import types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from db.engine import db_client
from handlers import router
from handlers.commands.auth import send_auth
from utils.messages import get_data


@router.message(Command("start"))
async def send_start(msg: types.Message, command: CommandObject, state: FSMContext):
    await db_client.get_or_create_user(telegram_id=msg.from_user.id,
                                       username=msg.from_user.username,
                                       name=msg.from_user.first_name,
                                       locale_alias=str(msg.from_user.language_code))
    await db_client.update_user_last_seen(telegram_id=msg.from_user.id,)

    if command.args:
        if command.args == "start-auth":
            await send_auth(msg=msg, state=state)
            return

    args = await get_data(msg, "start")
    args["text"]=args["text"].format(user=msg.from_user.username)
    await msg.answer(**args)
