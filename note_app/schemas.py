import datetime

from fastapi import Query
from pydantic import BaseModel, Field


class Paginator(BaseModel):
    limit: int | None = Field(Query(
        default=25,
        ge=5,
        le=50,
        description='Количество элементов в выдаче',
    ))
    page: int | None = Field(Query(
        default=1,
        ge=1,
        description='Номер страницы',
    ))


class NoteCreate(BaseModel):
    title: str
    content: str


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class NoteList(Note):
    pass


class NoteListUser(Note):
    user_name: str
