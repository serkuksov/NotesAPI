from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, Integer, Column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from setings import settings


class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True)


engine = create_engine(settings.SQL_URL, echo=True)
session_maker = sessionmaker(bind=engine)

async_engine = create_async_engine(settings.ASYNC_SQL_URL, echo=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with session_maker() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
