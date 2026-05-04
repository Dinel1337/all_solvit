import logging
from fastapi import FastAPI
from .api import router as start_router

from src._core.database import init_db
from .config import OpenAPI_text
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ...            
    except Exception as e:
        logger.error(f"Ошибка бд: {e}")
        raise
    yield
    

def create_app(lifespan_enabled=True):
    app = FastAPI(
        title="Quiz Platform",
        version="1.0.0",
        lifespan=lifespan if lifespan_enabled else None,
        description=OpenAPI_text,
        swagger_ui_parameters={
        "customCss": ".swagger-ui textarea { min-height: 500px !important; resize: vertical !important; }"}
    )

    app.include_router(start_router)

    return app

