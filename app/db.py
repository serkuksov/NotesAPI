from sqlalchemy import create_engine, Integer, ForeignKey, Column
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from setings import settings


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)


engine = create_engine(settings.SQL_URL, echo=True)
session_maker = sessionmaker(bind=engine)

async_engine = create_async_engine(settings.ASYNC_SQL_URL, echo=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
