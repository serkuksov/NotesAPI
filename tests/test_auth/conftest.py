from sqlalchemy import select

from auth.models import User
from tests.conftest import async_session_maker


async def get_user_from_database(user_id: int) -> User:
    async with async_session_maker() as session:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.fetchone()[0]
