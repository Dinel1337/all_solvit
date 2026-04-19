"""Глобальные фикстуры и конфигурация pytest для всех модулей.

Предоставляет:
- engine — асинхронный движок БД, создаёт схемы public/api_tracker/quiz_platform и таблицы перед тестами.
- db_session — транзакционная сессия с автоматическим откатом после каждого теста.
- test_reg, test_login — базовые данные для регистрации и входа.
- pytest_configure — очистка консоли, опциональный рестарт PostgreSQL (RESTART_PG=1).

Особенности:
- TESTING=1 устанавливается автоматически.
- Все таблицы создаются заново для каждого теста (function scope).
- Транзакции откатываются — БД остаётся чистой.
"""

import subprocess
import os
os.environ["TESTING"] = "1"
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src._core.database.database_alchemy.base import (
    PublicBase, ApiTrackerBase, QuizPlatformBase
)

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:dinelefox@localhost:5432/test_db"

def pytest_configure(config):
    os.system('clear')
    
    if os.environ.get("RESTART_PG") == "1":
        print("🔄 Перезагрузка PostgreSQL")
        subprocess.run(['sudo', 'service', 'postgresql', 'restart'], check=False)


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=None,
    )

    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS public"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS api_tracker"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS quiz_platform"))

        await conn.run_sync(PublicBase.metadata.create_all)
        await conn.run_sync(ApiTrackerBase.metadata.create_all)
        await conn.run_sync(QuizPlatformBase.metadata.create_all)

    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine, request):
    async with engine.connect() as conn:
        trans = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        
        yield session
        
        await trans.rollback()
        await session.close()
        
@pytest.fixture
def test_reg():
    return {
      "email": "user@gmail.com",
      "password": "Dinelefox",
      "username": "username"
    }

@pytest.fixture
def test_login():
    return {
  "password": "Dinelefox",
  "username": "username"
}
