
"""ДЛЯ ТЕСТОВ СОЗДАЮ ЭТОТ БЛОК, ЧТО БЫ НЕ ТЕСТИРОВАТЬ ОТДЕЛЬНО КАЖДЫЙ ПРОЕКТ"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from src._core.auth import authentication_router, AuthTokenMiddleware
from src._core.database import init_db, PublicBase

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db(PublicBase)
    except Exception as e:
        raise
    yield


def create_app(lifespan_enabled=True):
    app = FastAPI()

    app.include_router(authentication_router)
    app.add_middleware(AuthTokenMiddleware)

    return app