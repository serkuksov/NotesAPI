from typing import List

from sqlalchemy import Update, Delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, Session

from auth.models import User
from note_app.filters import NoteFilter
from .models import Note


def create_note(
    user_id: int,
    session: Session,
    title: str,
    content: str | None,
) -> Note:
    db_note = Note(user_id=user_id, title=title, content=content)
    session.add(db_note)
    session.commit()
    session.refresh(db_note)
    return db_note


def get_note(
    note_id: int,
    session: Session,
) -> Note | None:
    db_note = session.query(Note).filter_by(id=note_id).one_or_none()
    return db_note


def get_list_user_notes(
    user_id: int, session: Session, limit: int | None = 25, page: int | None = 1
) -> List[Note | None]:
    skip = (page - 1) * limit
    db_notes = (
        session.query(Note)
        .filter_by(user_id=user_id)
        .order_by(Note.updated_at.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )
    return db_notes


async def get_list_note(
    note_filter: NoteFilter,
    session: AsyncSession,
    limit: int | None = 25,
    page: int | None = 1,
) -> List[Note | None]:
    skip = (page - 1) * limit
    query = select(Note).join(User).options(contains_eager(Note.user))
    query = note_filter.filter(query)
    query = note_filter.sort(query)
    query = query.limit(limit).offset(skip)
    result = await session.execute(query)
    db_notes = result.scalars().all()
    return db_notes


def update_note_fields(
    note_id: int,
    session: Session,
    title: str = None,
    content: str = None,
) -> bool:
    stmt = Update(Note).filter_by(id=note_id)
    if title is not None:
        stmt = stmt.values(title=title)
    if content is not None:
        stmt = stmt.values(content=content)
    result = session.execute(stmt)
    session.commit()
    return result.rowcount > 0


def delete_note(
    note_id: int,
    session: Session,
) -> bool:
    stmt = Delete(Note).filter_by(id=note_id)
    result = session.execute(stmt)
    session.commit()
    return result.rowcount > 0
