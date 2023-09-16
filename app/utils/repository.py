from abc import ABC, abstractmethod

from sqlalchemy import insert, select

from db import async_session_maker, Base


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, elm_id: int):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = Base

    async def add_one(self, data: dict) -> int:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def find_one(self, elm_id: int):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.id == elm_id)
            res = await session.execute(stmt)
            res = res.scalar()
            return res
