from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from yandex_music import ClientAsync
from yandex_music.exceptions import UnauthorizedError

from db.engine import db_client
from handlers import router
from utils.messages import ask, auto_delete, get_data, next_step


class AuthState(StatesGroup):
    waiting_api_key = State()
    confirm_change_key = State()



@router.message(Command("auth"))
async def send_auth(msg: types.Message, state: FSMContext):
    if msg.chat.type != "private":
        await msg.answer(**await get_data(msg, "auth-only-private"))
        return

    if await db_client.check_auth(msg.chat.id):
        await msg.answer(**await get_data(msg, "auth-already"))
        await state.set_state(AuthState.confirm_change_key)
        return

    await msg.answer(**await get_data(msg, "auth-request"))
    await state.set_state(AuthState.waiting_api_key)


@router.message(AuthState.waiting_api_key)
async def process_api_key(msg: types.Message, state: FSMContext):
    if await next_step(msg):
        api_key = msg.text.strip()
        status = await msg.answer(**await get_data(msg, "auth-checkout"))
        await auto_delete(msg, 0)
        try:
            await ClientAsync(api_key).init()
            await db_client.add_key(msg.chat.id, api_key)
            await msg.bot.edit_message_text(**await get_data(msg, "auth-checkout-success"),
                                            chat_id=msg.chat.id,
                                            message_id=status.message_id)
            await state.clear()
            await auto_delete(status)
            return
        except UnauthorizedError:
            await msg.bot.edit_message_text(**await get_data(msg, "auth-checkout-fail"),
                                            chat_id=msg.chat.id,
                                            message_id=status.message_id)
            await state.clear()
            await auto_delete(status)
            return

    msg = await msg.answer(**await get_data(msg, "close-response"))
    await state.clear()
    await auto_delete(msg)


@router.message(AuthState.confirm_change_key)
async def confirm_changing(msg: types.Message, state: FSMContext):
    if await ask(msg):
        await msg.answer(**await get_data(msg, "auth-request"))
        await state.set_state(AuthState.waiting_api_key)
    else:
        msg = await msg.answer(**await get_data(msg, "no-answer"))
        await state.clear()
        await auto_delete(msg)
