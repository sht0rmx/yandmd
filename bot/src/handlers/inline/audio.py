from aiogram import types

from db.engine import db_client
from handlers import router
from utils.inline_answers import Icons, add_audio_track, add_text_result, add_text_track
from utils.track import get_now_playing_track
from utils.translate import translations


@router.inline_query()
async def inline_handler(query: types.InlineQuery):
    user = await db_client.get_user(query.from_user.id)
    lang = user.locale_alias if user else "en"

    if not user or not await db_client.check_auth(query.from_user.id):
        await query.answer(
            results=[],
            switch_pm_text=await translations.t(msg_id="change-pm", lang_base=lang),
            switch_pm_parameter="start-auth",
            cache_time=0,
        )
        return

    elif query.query.strip().lower() == "audio":
        try:
            track = await get_now_playing_track(user.api_key)
            results = [add_audio_track(track)]
            await query.answer(results=results, cache_time=0)
        except ValueError:
            await query.answer(results=[await add_text_result(Icons.ERROR, "inline-error", "error-fetching", lang)], cache_time=0)

    elif query.query.strip().lower() == "text":
        try:
            track = await get_now_playing_track(user.api_key)
            results = [add_text_track(track)]
            await query.answer(results=results, cache_time=0)
        except ValueError:
            await query.answer(results=[await add_text_result(Icons.ERROR, "inline-error", "error-fetching", lang)], cache_time=0)

    elif query.query.strip().startswith("https://music.yandex.ru"):
        try:
            track = await get_now_playing_track(user.api_key, query.query.strip())
            results = [add_text_track(track), add_audio_track(track)]
            await query.answer(results=results, cache_time=0)
        except ValueError:
            await query.answer(results=[await add_text_result(Icons.ERROR, "inline-error", "error-fetching", lang)], cache_time=0)

    else:
        results = [
            await add_text_result(Icons.AUDIO, "inline-audio", "send-audio", lang),
            await add_text_result(Icons.TEXT, "inline-text", "send-text", lang),
            await add_text_result(Icons.LINK, "inline-link", "send-by-link", lang)
        ]

        await query.answer(results=results, cache_time=0)
