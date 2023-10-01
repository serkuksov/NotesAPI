import pytest
from httpx import AsyncClient
from sqlalchemy import select

from auth.models import User
from tests.conftest import async_session_maker


async def get_user_from_database(user_id: int) -> User | None:
    async with async_session_maker() as session:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


@pytest.fixture(autouse=True, scope="session")
async def create_user_in_database(async_client: AsyncClient):
    data_user_1 = {
        "email": "test_user_1@example.com",
        "user_name": "test_user_1",
        "password": "string",
    }
    response = await async_client.post("/auth/register", json=data_user_1)
    assert response.status_code == 201

    data_user_2 = {
        "email": "test_user_2@example.com",
        "user_name": "test_user_2",
        "password": "string",
    }
    response = await async_client.post("/auth/register", json=data_user_2)
    assert response.status_code == 201
