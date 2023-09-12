from typing import Optional

from fastapi import Query
from fastapi_filter import FilterDepends
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field

from auth.models import User
from note_app.models import Note


class UserFilter(Filter):
    user_name__like: Optional[str] = Field(
        Query(
            alias="user",
            default=None,
            description="Фильтр по части имени пользователя",
        )
    )

    class Constants(Filter.Constants):
        model = User


class NoteFilter(Filter):
    title: Optional[str] = Field(
        Query(
            default=None,
            description="Фильтр по названию заметки",
        )
    )
    user: Optional[UserFilter] = FilterDepends(UserFilter)
    order_by: Optional[list[str]] = Field(
        Query(
            default="-created_at,+title",
            description="Сортировка по дате создания и названию заметки, "
            "+ в порядке возрастания, - в порядке убывания",
        )
    )
    search: Optional[str] = Field(
        Query(
            default=None,
            description="Поиск по части title или content",
        )
    )

    class Constants(Filter.Constants):
        model = Note
        search_model_fields = ["title", "content"]
