from fastapi import FastAPI

from auth.routers import user_router
from note_app.routers import note_router


app = FastAPI(
    title="NotesAPI",
    description="API реализующее CRUD для заметок пользователей.\n"
    "Авторизация пользователей с использованием JWT токенов",
)

app.include_router(user_router)
app.include_router(note_router)
