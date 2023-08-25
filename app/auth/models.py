from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTable
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship

from app.batadase import Base, async_session_maker


class User(SQLAlchemyBaseUserTable[int], Base):
    user_name = Column(String(60), nullable=False, unique=True)

    notes = relationship('Note', overlaps="user")

    def __str__(self):
        return self.user_name


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
