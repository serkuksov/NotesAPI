from note_app.models import Note
from utils.repository import SQLAlchemyRepository


class NotesRepository(SQLAlchemyRepository):
    model = Note
