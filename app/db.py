from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

from setings import settings


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_engine(settings.SQL_URL, echo=True)
session_maker = sessionmaker(bind=engine)

async_engine = create_async_engine(settings.ASYNC_SQL_URL, echo=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[Session, None]:
    async with async_session_maker() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
