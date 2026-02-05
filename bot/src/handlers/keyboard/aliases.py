from aiogram import types

from db.engine import db_client
from handlers import router
from handlers.commands.auth import send_auth
from handlers.commands.help import send_help
from handlers.commands.start import send_start
from handlers.commands.track import send_now_track


@router.callback_query(lambda q: q.data and q.data.startswith("command:"))
async def callback_command(query: types.CallbackQuery):
    cmd = query.data.split(":", 1)[1]

    if cmd == "start":
        await send_start(query.message)
    elif cmd == "help":
        await send_help(query.message)
    elif cmd == "auth":
        await send_auth(query.message)
    elif cmd == "now":
        await send_now_track(query.message)
    elif cmd == "stats":
        user = await db_client.get_user(query.message.chat.id)
        if user:
            await query.answer(
                text=f"👤 {user.username}\n🎵 sent: {user.total_tracks} track(s)",
                show_alert=True
            )
    await query.answer()
