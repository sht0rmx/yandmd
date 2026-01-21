import os
import tempfile

import aiohttp
from aiogram import F, types
from aiogram.filters import Command
from aiogram.types import InputFile
from mutagen.id3 import APIC, ID3, TIT2, TPE1, USLT
from mutagen.mp3 import MP3

from db.engine import db_client
from handlers import router
from utils.messages import get_data
from utils.track import extract_track_id, fetch_now_playing_track_id, fetch_track


async def download_track(track):
    async with aiohttp.ClientSession() as session:
        async with session.get(track.track_url) as resp:
            if resp.status != 200:
                return None
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp_file.write(await resp.read())
            tmp_file.close()
            return tmp_file.name

async def embed_tags(file_path, track):
    audio = MP3(file_path, ID3=ID3)
    try:
        audio.add_tags()
    except Exception:
        pass

    audio.tags.add(TIT2(encoding=3, text=track.title))
    audio.tags.add(TPE1(encoding=3, text=track.artist))

    comment_text = f"Я.Музыка: {track.ya_link}"
    if track.songlink:
        comment_text += f" • songlink: {track.songlink}"
    audio.tags.add(USLT(encoding=3, text=comment_text, desc='info'))

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://{track.cover_url}") as resp:
            if resp.status == 200:
                cover_data = await resp.read()
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # front cover
                    desc='cover',
                    data=cover_data
                ))

    audio.save()

@router.message(Command("now"))
async def send_now_track(msg: types.Message):
    user = await db_client.get_user(msg.from_user.id)

    if not user or not await db_client.check_auth(msg.from_user.id):
        await msg.answer(**await get_data(msg, "auth-required"))
        return

    track_id = fetch_now_playing_track_id(user.api_key)
    if not track_id:
        await msg.answer(**await get_data(msg, "track-not-found"))
        return

    progress = await msg.answer(**await get_data(msg, "track-downloading"))

    track = await fetch_track(user.api_key, track_id)
    if not track:
        await progress.edit_text(**await get_data(msg, "track-fetch-error"))
        return

    file_path = await download_track(track)
    if not file_path:
        await progress.edit_text(**await get_data(msg, "track-download-error"))
        return

    await embed_tags(file_path, track)

    await msg.answer_audio(
        audio=InputFile(file_path),
        title=track.title,
        performer=track.artist,
    )

    await progress.delete()
    os.remove(file_path)


@router.message(
    F.text.regexp(r'https?://(?:music\.)?yandex\.ru/.+(?:track|album/\d+/track)/\d+')
)
async def handle_track_link(msg: types.Message):
    user = await db_client.get_user(msg.from_user.id)

    if not user or not await db_client.check_auth(msg.from_user.id):
        await msg.answer(**await get_data(msg, "auth-required"))
        return

    track_id = extract_track_id(msg.text)
    if not track_id:
        await msg.answer(**await get_data(msg, "track-not-found"))
        return

    progress = await msg.answer(**await get_data(msg, "track-downloading"))

    track = await fetch_track(user.api_key, track_id)
    if not track:
        await progress.edit_text(**await get_data(msg, "track-fetch-error"))
        return

    file_path = await download_track(track)
    if not file_path:
        await progress.edit_text(**await get_data(msg, "track-download-error"))
        return

    await embed_tags(file_path, track)

    await msg.answer_audio(
        audio=InputFile(file_path),
        title=track.title,
        performer=track.artist,
    )

    await progress.delete()
    os.remove(file_path)
