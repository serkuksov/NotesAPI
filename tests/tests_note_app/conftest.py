import pytest
from sqlalchemy import Insert

from note_app.models import Note
from tests.conftest import async_session_maker


@pytest.fixture(scope="module")
def test_notes() -> list[dict]:
    test_notes = []
    for i in range(30):
        test_notes.append(
            {
                "title": f"test_title_{i}",
                "content": f"test_content_{i}",
                "user_id": i % 2 + 1,
            }
        )
    return test_notes


@pytest.fixture(scope="module", autouse=True)
async def create_note(test_notes: list[dict]):
    async with async_session_maker() as session:
        query = Insert(Note).values(test_notes)
        await session.execute(query)
        await session.commit()
