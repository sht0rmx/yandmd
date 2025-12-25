import json
import os

from aiogram import types

from db.engine import db_client
from utils.logging import logger


class TranslationManager:
    def __init__(self, path="src/locales"):
        logger.debug(f"[Translations] app workdir: {os.getcwd()}")
        self.path = path
        self.data = {}
        self.load_all()

    def load_all(self):
        try:
            for file in os.listdir(self.path):
                if file.endswith(".json"):
                    with open(os.path.join(self.path, file), encoding="utf-8") as f:
                        lang = json.load(f)
                        alias = lang.get("lang-alias")
                        if alias:
                            self.data[alias] = lang
            logger.info(f"Loaded {len(self.data)} language packs")
        except Exception as e:
            logger.error(f"Error loading translations: {e}")

    async def t(self, message:types.Message | None=None, msg_id:str="",uid: int | None=None, lang="en", lang_base: str | None=None):
        try:
            if lang_base:
                user_lang = lang_base
            elif not uid and message:
                user = message.from_user
                if not user.is_bot:
                    user_lang = getattr(user, "language_code", lang)
                else:
                    result = await db_client.get_user(message.chat.id)
                    user_lang = result.locale_alias if result else lang
            else:
                result = await db_client.get_user(uid)
                user_lang = result.locale_alias if result else lang

            user_lang = (user_lang if user_lang else lang)[:2]

            lang_data = self.data.get(user_lang, self.data.get(lang))
            if not lang_data:
                logger.warning(f"Lang '{user_lang}' not found, fallback to '{lang}'")
                return msg_id
            return lang_data["messages"].get(msg_id)
        except Exception as e:
            logger.error(f"Error getting translation '{msg_id}': {e}")
            return msg_id


translations = TranslationManager()
