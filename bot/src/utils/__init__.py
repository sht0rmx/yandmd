import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from utils.logging import logger

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def dump_router(dp, prefix: str = "") -> None:
    for event, observer in dp.observers.items():
        if not observer.handlers:
            continue
        logger.debug(f"{prefix}{event}:")
        for h in observer.handlers:
            logger.debug(f"{prefix}  - {h.callback.__module__}.{h.callback.__name__}")

    for sub in getattr(dp, "sub_routers", []):
        dump_router(sub, "  ")



async def bot_info() -> None:
    try:
        me = await bot.get_me()
        logger.info(f"Bot '{me.full_name}' started")
        logger.info(f"Username: @{me.username}")
        logger.info(f"Bot ID: {me.id}")
    except Exception as e:
        logger.error(f"Error in bot_info: {e}")
