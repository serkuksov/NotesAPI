from abc import ABC, abstractmethod
from typing import Any, Sequence

from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import insert, select, update, delete, Select

from db import async_session_maker, Base


class AbstractRepository(ABC):
    """Абстрактный репозиторий"""

    @abstractmethod
    async def add_one(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, elm_id: int):
        raise NotImplementedError

    @abstractmethod
    async def update_elm(self, elm_id: int, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_elm(self, elm_id: int):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, limit: int, page: int):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = Base

    async def add_one(self, **kwargs) -> Any:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**kwargs).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar()

    async def find_one(self, elm_id: int) -> Any | None:
        async with async_session_maker() as session:
            query = select(self.model).where(self.model.id == elm_id)
            res = await session.execute(query)
            return res.scalar_one_or_none()

    async def update_elm(self, elm_id: int, **kwargs) -> bool:
        async with async_session_maker() as session:
            stmt = update(self.model).where(self.model.id == elm_id)
            if kwargs is not None:
                stmt = stmt.values(**kwargs)
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0

    async def delete_elm(self, elm_id: int) -> bool:
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.id == elm_id)
            res = await session.execute(stmt)
            await session.commit()
            return res.rowcount > 0

    def find_all(self, limit: int, page: int):
        query = self.get_query()
        return self.pagination_query(query=query, limit=limit, page=page)

    @staticmethod
    async def _find_elements(
        query: Select,
        filter_elm: Filter | None,
        limit: int,
        page: int,
    ) -> Sequence[Any]:
        skip = (page - 1) * limit
        async with async_session_maker() as session:
            if filter_elm is not None:
                query = filter_elm.filter(query)
                if hasattr(filter_elm, "order_by"):
                    query = filter_elm.sort(query)
            query = query.limit(limit).offset(skip)
            res = await session.execute(query)
            return res.scalars().all()

    def get_query(self) -> Select:
        return select(self.model)

    @staticmethod
    def pagination_query(query: Select, limit: int, page: int) -> Select:
        skip = (page - 1) * limit
        return query.limit(limit).offset(skip)

    async def find_elements(
        self,
        filter_elm: Filter | None = None,
        limit: int = 25,
        page: int = 1,
    ) -> Sequence[Any]:
        return await self._find_elements(
            query=self.get_query(),
            filter_elm=filter_elm,
            limit=limit,
            page=page,
        )
