from dataclasses import dataclass

from aiogram.enums import ParseMode
from aiogram.types import (
    InlineQueryResultArticle,
    InlineQueryResultAudio,
    InputTextMessageContent,
)

from utils.track import TrackData
from utils.translate import translations


@dataclass
class Icons:
    ERROR: str = "https://img.icons8.com/?size=100&id=DXECg4JU1n2x&format=png&color=000000"
    AUDIO: str = "https://img.icons8.com/?size=100&id=VmIchBapvMDA&format=png&color=000000"
    TEXT: str = "https://img.icons8.com/?size=100&id=7Toxu00bPFMa&format=png&color=000000"
    LINK: str = "https://img.icons8.com/?size=100&id=QYd5yJnmjVdK&format=png&color=000000"


def add_audio_track(track: TrackData):
    return InlineQueryResultAudio(
            id=f"audio_{track.track_id}",
            audio_url=track.track_url,
            title=track.title,
            performer=track.artist,
            thumbnail_url=track.cover_url,
            caption=f"[Я.Музыка]({track.ya_link}) • [songlink]({track.songlink})" if track.songlink else f"[Я.Музыка]({track.ya_link})",
            parse_mode=ParseMode.MARKDOWN,
        )

def add_text_track(track: TrackData):
    text = f"{track.title} - {track.artist}\n[Я.Музыка]({track.ya_link})"
    if track.songlink:
        text += f" • [songlink]({track.songlink})"

    return InlineQueryResultArticle(
        id=f"text_{track.track_id}",
        title=track.title,
        description=track.artist,
        thumbnail_url=track.cover_url,
        input_message_content=InputTextMessageContent(
            message_text=text,
            parse_mode=ParseMode.MARKDOWN
        )
    )

async def add_text_result(icon:str, header: str, description: str, lang: str):
    return InlineQueryResultArticle(
            id=f"text_{header}",
            title=await translations.t(msg_id=header, lang_base=lang),
            description=await translations.t(msg_id=description, lang_base=lang),
            thumbnail_url=icon,
            input_message_content=InputTextMessageContent(
                message_text="Больше в @yandmdbot"),
        )
