import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src._core.auth import authentication_router, AuthTokenMiddleware
from src._core.database import init_db, DatabaseManager, ApiTrackerBase

from .config import OpenAPI_text
from .local_core.repository import ExerciseRepository
from .local_core.service import ExerciseService
from .api import router as start_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # await init_db(PublicBase)
        await init_db(ApiTrackerBase)

        session_maker = DatabaseManager.get_session_maker()

        async with session_maker() as db:
            repo = ExerciseRepository(db)
            service = ExerciseService(repo)
            await service.get_hash_database()

    except Exception as e:
        logger.error(f"Ошибка БД: {e}")
        raise

    yield


def create_app(lifespan_enabled=True):
    app = FastAPI(
        title="API Tracker",
        version="1.0.0",
        lifespan=lifespan if lifespan_enabled else None,
        description=OpenAPI_text,
    )

    app.include_router(authentication_router)
    app.include_router(start_router)
    app.add_middleware(AuthTokenMiddleware)

    return app