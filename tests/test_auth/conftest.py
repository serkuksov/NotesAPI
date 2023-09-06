from httpx import AsyncClient
from sqlalchemy import select

from auth.models import User
from tests.conftest import async_session_maker


async def get_user_from_database(user_id: int) -> User:
    async with async_session_maker() as session:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.fetchone()[0]


async def get_jwt_token_authorized_user(async_client: AsyncClient) -> str:
    data_user = {
        'username': 'user@example.com',
        'password': 'string',
    }
    response = await async_client.post('/auth/jwt/login', data=data_user)
    data_from_response = response.json()
    return data_from_response["access_token"]
