from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.exceptions import RequestValidationError
from fastapi_filter import FilterDepends

from auth.auth import current_active_user
from auth.models import User
from note_app import models, schemas, filters
from note_app.repositorie import NotesRepository

note_router = APIRouter(prefix="/notes", tags=["Note"])


@note_router.get(
    "/",
    response_model=list[schemas.NoteListUser],
    responses={
        200: {"description": "Успешный ответ"},
    },
)
async def get_list_note(
    filter_note: filters.NoteFilter = FilterDepends(filters.NoteFilter),
    pagination: schemas.Paginator = Depends(schemas.Paginator),
) -> list[schemas.NoteListUser]:
    """
    Возвращает список всех заметок совместно с информацией о создавшем пользователе
    """
    try:
        res = await NotesRepository().find_notes_with_users(
            filter_elm=filter_note,
            **pagination.dict(),
        )
    except RequestValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Переданы не корректные данные для сортировки",
        )
    # TODO необходимо избавится от конструкции с генераторм списков
    return [
        schemas.NoteListUser(user_name=elm.user.user_name, **elm.__dict__)
        for elm in res
    ]


@note_router.get(
    "/user/",
    response_model=list[schemas.NoteList],
    responses={
        200: {"description": "Успешный ответ"},
        401: {"description": "Unauthorized"},
    },
)
async def get_list_note_user(
    user: User = Depends(current_active_user),
    pagination: schemas.Paginator = Depends(schemas.Paginator),
) -> list[models.Note | None]:
    """
    Возвращает список всех заметок конкретного пользователя
    """
    filter_note = filters.NoteFilterByUserId(user_id=user.id)
    return await NotesRepository().find_elements(
        filter_elm=filter_note,
        **pagination.dict(),
    )


@note_router.get(
    "/{note_id}/",
    response_model=schemas.Note,
    responses={
        200: {"description": "Успешный ответ"},
        404: {"description": "Объект с идентификатором id не найден"},
    },
)
async def get_note_by_id(
    note_id: int,
) -> models.Note:
    """
    Возвращает информацию о заметке по ее идентификатору
    """
    note = await NotesRepository().find_one(elm_id=note_id)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Объект с идентификатором {note_id} не найден",
        )
    return note


@note_router.post(
    "/",
    response_model=schemas.Note,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Объект успешно создан"},
    },
)
async def cerate_note(
    note: Annotated[schemas.NoteCreate, Body()],
    user: User = Depends(current_active_user),
) -> models.Note:
    """
    Создание новой заметки
    """
    return await NotesRepository().add_one(user_id=user.id, **note.dict())


@note_router.put(
    "/{note_id}/",
    responses={
        200: {"description": "Объект с идентификатором id успешно обновлен"},
        400: {"description": "Не переданы параметры для обновления объекта"},
        403: {"description": "У пользователя не достаточно прав"},
        404: {"description": "Объект с идентификатором id не найден"},
    },
)
async def update_note(
    note_id: int,
    note: Annotated[schemas.NoteUpdate, Body()],
    user: User = Depends(current_active_user),
) -> str:
    """
    Обновление заметки.
    """
    note_db = await NotesRepository().find_one(elm_id=note_id)

    # Проверка наличия заметки
    if not note_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Объект с идентификатором {note_id} не найден",
        )

    # Проверка прав доступа
    if user.id != note_db.user_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Отсутствуют права на редактирование объекта",
        )
    note_param = note.dict(exclude_none=True)

    # Проверка что хотябы одно поле передано
    if not note_param:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не переданы параметры для обновления объекта",
        )

    await NotesRepository().update_elm(elm_id=note_id, **note_param)
    return f"Объект с идентификатором {note_id} успешно обновлен"


@note_router.delete(
    "/{note_id}/",
    responses={
        200: {"description": "Объект с идентификатором id успешно удален"},
        403: {"description": "Отсутствуют права на удаление объекта"},
        404: {"description": "Объект с идентификатором id не найден"},
    },
)
async def delete_note(
    note_id: int,
    user: User = Depends(current_active_user),
) -> str:
    """
    Удаление заметки
    """
    note_db = await NotesRepository().find_one(elm_id=note_id)

    # Проверка наличия заметки
    if not note_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Объект с идентификатором {note_id} не найден",
        )

    # Проверка прав доступа
    if user.id != note_db.user_id and not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Отсутствуют права на удаление объекта",
        )

    await NotesRepository().delete_elm(elm_id=note_id)
    return f"Объект с идентификатором {note_id} успешно удален"
