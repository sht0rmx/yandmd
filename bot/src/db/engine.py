import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from db.models import Base
from db.models.Users import User
from utils.logging import logger

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(str(DATABASE_URL), echo=False)


class DBError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class NotFound(DBError):
    pass

class Database:
    def __init__(self):
        self.engine = engine
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    #Db
    async def create_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()

    # User
    async def get_user(self, telegram_id: int) -> User | None:
        async with self.async_session() as dbsession:
            result = await dbsession.execute(select(User).where(User.telegram_id == telegram_id))
            return result.scalar_one_or_none()

    async def create_user(
        self,
        telegram_id: int,
        username: str | None = None,
        name: str | None = None,
        role: str = "user",
        avatar_url: str | None = None,
        locale_alias: str | None = "en",
        api_key: str | None = None
    ) -> User:
        logger.debug(f"creating user {telegram_id}")
        async with self.async_session() as dbsession:
            user = User(
                telegram_id=telegram_id,
                username=username,
                name=name,
                role=role,
                avatar_url=avatar_url,
                locale_alias=locale_alias,
                api_key=api_key,
            )
            dbsession.add(user)
            await dbsession.commit()
            await dbsession.refresh(user)
            return user

    async def get_or_create_user(self, telegram_id: int, **kwargs) -> User:
        user = await self.get_user(telegram_id)
        if user:
            return user
        return await self.create_user(telegram_id, **kwargs)

    async def update_user_locale(self, telegram_id: int, locale_alias: str) -> None:
        async with self.async_session() as dbsession:
            result = await dbsession.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            if not user:
                raise NotFound(f"User {telegram_id} not found")
            user.locale_alias = locale_alias
            await dbsession.commit()

    async def update_user_last_seen(self, telegram_id: int) -> None:
        async with self.async_session() as dbsession:
            result = await dbsession.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            if not user:
                raise NotFound(f"User {telegram_id} not found")
            user.last_seen = datetime.utcnow()
            await dbsession.commit()

    async def check_auth(self, telegram_id: int) -> bool:
        user = await self.get_user(telegram_id=telegram_id)
        if user.api_key:
            return True
        else:
            return False

    async def add_key(self, telegram_id: int, api_key:str) -> None:
        async with self.async_session() as dbsession:
            await dbsession.execute(update(User).where(User.telegram_id == telegram_id).values(api_key=api_key))
            await dbsession.commit()

db_client = Database()
