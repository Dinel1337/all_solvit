import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src._core.auth.app import create_app
from src._core.database.database_alchemy.session import get_db

@pytest_asyncio.fixture
def app():
    return create_app(lifespan_enabled=False)

@pytest_asyncio.fixture
async def auth_client(app: FastAPI, db_session):
    async def override_get_db():
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def auth_client_setup(auth_client, test_reg, test_login):
    await auth_client.post("/auth/register", json=test_reg)
    await auth_client.post("/auth/login", json=test_login)
    return auth_client