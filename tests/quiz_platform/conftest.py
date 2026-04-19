import pytest_asyncio
import pytest
import asyncio


from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from src.quiz_platform.app import create_app
from src._core.database.database_alchemy.session import get_db

        
@pytest_asyncio.fixture
def app():
    return create_app(lifespan_enabled=False)

@pytest_asyncio.fixture
async def api_tracker_client(app: FastAPI, db_session):
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
    await asyncio.sleep(0.01)

@pytest_asyncio.fixture
async def quiz_platform_setup(api_tracker_client, test_reg, test_login):
    await api_tracker_client.post("/auth/register", json=test_reg)
    await api_tracker_client.post("/auth/login", json=test_login)
    return api_tracker_client

@pytest.fixture
def add_quiz():
    return{
  "description": "Тест по основам Python",
  "name": "Python Basics Quiz",
  "questions": [
    {
      "options": [
        {
          "is_correct": False,
          "text": "3"
        },
        {
          "is_correct": True,
          "text": "4"
        },
        {
          "is_correct": False,
          "text": "5"
        }
      ],
      "order": 0,
      "points": 2,
      "text": "Что выведет print(2 + 2)?"
    },
    {
      "options": [
        {
          "is_correct": False,
          "text": "int"
        },
        {
          "is_correct": True,
          "text": "str"
        },
        {
          "is_correct": False,
          "text": "list"
        }
      ],
      "order": 1,
      "points": 1,
      "text": "Какой тип данных у 'hello'?"
    }
  ],
  "status": "published"
}
    