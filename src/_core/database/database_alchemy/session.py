import os
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from global_config import ECHO
from src.config import Settings

setting = Settings()
logger = logging.getLogger("uvicorn")

TESTING = os.getenv("TESTING") == "1"


class DatabaseManager:
    _engine = None
    _session_maker = None

    @classmethod
    def reset(cls):
        cls._engine = None
        cls._session_maker = None

    @classmethod
    def get_database_url(cls) -> str:
        url = setting.DATABASE_URL_asyncpg
        if not url:
            raise ValueError("DATABASE_URL не задана")
        return url.strip(" '\"")

    @classmethod
    def get_engine(cls):
        """
        ВАЖНО:
        В тестах ВСЕГДА новый engine (никакого кеша и никакого asyncpg reuse)
        """
        url = cls.get_database_url()

        if TESTING:
            return create_async_engine(
                url,
                echo=ECHO,
                poolclass=None,
            )

        if cls._engine is None:
            cls._engine = create_async_engine(
                url,
                echo=ECHO,
                pool_pre_ping=True,
            )

        return cls._engine

    @classmethod
    def get_session_maker(cls):
        engine = cls.get_engine()

        if TESTING:
            return sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

        if cls._session_maker is None:
            cls._session_maker = sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

        return cls._session_maker


async def get_db():
    session_maker = DatabaseManager.get_session_maker()
    async with session_maker() as session:
        yield session


async def init_db(base: DeclarativeBase):
    """
    В тестах можно вызывать, но engine уже будет локальный (из тестов override'а)
    """
    engine = DatabaseManager.get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)