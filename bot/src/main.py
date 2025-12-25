import asyncio

from db.engine import db_client
from handlers import router
from utils import bot, bot_info, dp
from utils.logging import logger


async def main():
    try:
        logger.debug("creating db...")
        await db_client.create_db()
    except Exception:
        logger.error("can`t connect to database!")
        return

    await bot.delete_webhook(drop_pending_updates=True)

    dp.include_router(router)

    await bot_info()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped manually")
