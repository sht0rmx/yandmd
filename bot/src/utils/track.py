import re
from typing import NamedTuple

import requests
from odesli.Odesli import Odesli
from yandex_music import ClientAsync, Track

from utils import logger

_TRACK_RE = re.compile(r'(?:track/|album/\d+/track/)(\d+)')


class TrackData(NamedTuple):
    track_id: int
    track_url: str
    title: str
    artist: str
    album: str
    ya_link: str
    songlink: str | None
    cover_url: str | None = None


def extract_track_id(text: str) -> int:
    match = _TRACK_RE.search(text)
    return int(match.group(1)) if match else None


def fetch_now_playing_track_id(api_key: str) -> int | None:
    data = requests.get("http://server:9865/get_current_track_alpha", headers={"Authorization": f"OAuth {api_key}"})
    if data.status_code != 200:
        return None
    json_data = data.json()
    return json_data.get("track_id")


async def get_now_playing_track(api_key: str, query: str | None=None) -> TrackData:
    if query is None:
        track_id = fetch_now_playing_track_id(api_key)
    else:
        track_id = extract_track_id(query)

    if not track_id:
        raise ValueError("No track ID found")

    track = await fetch_track(api_key, track_id)
    if not track:
        raise ValueError("Error fetching track")

    return track


async def fetch_track(api_key: str, track_id: int) -> TrackData | None:
    try:
        client = await ClientAsync(api_key).init()
        tracks = await client.tracks([track_id])
        track: Track | None = tracks[0] if tracks else None
        if not track:
            return None

        download_info = await track.get_download_info_async(get_direct_links=True)
        if not download_info:
            return None

        url = await download_info[0].get_direct_link_async()

        title = track.title + (f" ({track.version})" if track.version else "")
        artist = ", ".join([artist.name for artist in track.artists]) if track.artists else "Unknown"
        album = ", ".join([album.title for album in track.albums]) if track.albums else "Single"
        ya_link = f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}"
        cover_url = track.cover_uri.replace("%%", "1000x1000") if track.cover_uri else None

        songlink = None
        try:
            songlink = Odesli().getByUrl(ya_link).songLink
        except Exception:
            pass

        return TrackData(
            track_id=track.id,
            track_url=url,
            title=title,
            artist=artist,
            album=album,
            ya_link=ya_link,
            songlink=songlink,
            cover_url=cover_url,
        )

    except Exception as e:
        logger.error(f"fetch_track error: {e}")
        return None
