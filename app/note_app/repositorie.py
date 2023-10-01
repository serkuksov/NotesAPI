from typing import Sequence, Any

from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy.orm import contains_eager

from auth.models import User
from note_app.models import Note
from utils.repository import SQLAlchemyRepository


class NotesRepository(SQLAlchemyRepository):
    model = Note

    async def find_notes_with_users(
        self,
        filter_elm: Filter | None = None,
        limit: int = 25,
        page: int = 1,
    ) -> Sequence[Any]:
        query = self.get_query().join(User).options(contains_eager(Note.user))
        return await self._find_elements(
            query=query,
            filter_elm=filter_elm,
            limit=limit,
            page=page,
        )
