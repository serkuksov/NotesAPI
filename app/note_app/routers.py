from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from auth.auth import current_active_user
from auth.models import User
from db import get_async_session, get_session
from note_app import crud, models, schemas, filters

note_router = APIRouter(prefix='/notes', tags=['Note'])


@note_router.get(
    '/',
    # response_model=list[schemas.NoteListUser],
    responses={
        200: {'description': 'Успешный ответ'},
    }
)
async def get_list_note(
        note_filter: filters.NoteFilter = FilterDepends(filters.NoteFilter),
        pagination: schemas.Paginator = Depends(schemas.Paginator),
        session: AsyncSession = Depends(get_async_session),
) -> list[schemas.NoteListUser]:
    """
    Возвращает список всех заметок совместно с информацией о создавшем пользователе
    """
    result = await crud.get_list_note(note_filter, session,  **pagination.dict())
    return [schemas.NoteListUser(user_name=elm.user.user_name, **elm.__dict__) for elm in result]


@note_router.get(
    '/user/{user_id}/',
    response_model=list[schemas.NoteList],
    responses={
        200: {'description': 'Успешный ответ'},
    }
)
def get_list_note_user(
        user_id: int,
        pagination: schemas.Paginator = Depends(schemas.Paginator),
        session: Session = Depends(get_session),
) -> list[models.Note]:
    """
    Возвращает список всех заметок конкретного пользователя
    """
    return crud.get_list_user_notes(user_id, session, **pagination.dict())


@note_router.get(
    '/{note_id}',
    response_model=schemas.Note,
    responses={
        200: {'description': 'Успешный ответ'},
        404: {'description': 'Объект с указаным id не найден'},
    }
)
def get_note(
        note_id: int,
        session: Session = Depends(get_session),
) -> models.Note:
    """
    Возвращает информацию о заметке по ее идентификатору
    """
    note = crud.get_note(note_id, session)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Заметка с идентификатором {note_id} не найдена'
        )
    return note


@note_router.post(
    '/',
    response_model=schemas.Note,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {'description': 'Объект успешно создан'},
    }
)
def cerate_note(
        note: Annotated[schemas.NoteCreate, Body()],
        user: User = Depends(current_active_user),
        session: Session = Depends(get_session),
) -> models.Note:
    """
    Создание новой заметки
    """
    return crud.create_note(user.id, session, **note.dict())


@note_router.put(
    '/{note_id}/',
    responses={
        200: {'description': 'Объект успешно обнавлен'},
        400: {'description': 'Не переданы параметры для обнавления'},
        403: {'description': 'У пользователя не достаточно прав'},
        404: {'description': 'Объект с указаным id не найден'},
    }
)
def update_note(
        note_id: int,
        note: schemas.NoteUpdate = Depends(schemas.NoteUpdate),
        user: User = Depends(current_active_user),
        session: Session = Depends(get_session),
) -> str:
    """
    Обновление заметки.
    """
    existing_note = crud.get_note(note_id, session)

    # Проверка наличия заметки
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Заметка с идентификатором {note_id} не найдена'
        )

    # Проверка прав доступа
    if user.id != existing_note.user_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Отсутствуют права на редактирование заметки'
        )

    # Обновление полей заметки
    if note.title or note.content:
        crud.update_note_fields(note_id, session, **note.dict())
        return 'Заметка с идентификатором {note_id} успешно обновлена'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Не переданы параметры для обновления заголовка или содержимого заметки'
        )


@note_router.delete(
    '/{note_id}/',
    responses={
        200: {'description': 'Объект успешно удален'},
    }
)
def delete_note(
        note_id: int,
        user: User = Depends(current_active_user),
        session: Session = Depends(get_session),
) -> str:
    """
    Удаление заметки
    """
    existing_note = crud.get_note(note_id, session)

    # Проверка наличия заметки
    if not existing_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Заметка с идентификатором {note_id} не найдена'
        )

    # Проверка прав доступа
    if user.id != existing_note.user_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Отсутствуют права на редактирование заметки'
        )
    if crud.delete_note(note_id, session):
        return f'Заметка с идентификатором {note_id} успешно удалена'
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Заметка с идентификатором {note_id} не найдена'
        )
