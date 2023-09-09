from httpx import AsyncClient
from sqlalchemy import select

from note_app.models import Note
from tests.conftest import async_session_maker
from tests.test_auth.conftest import jwt_token


class TestCreateNote:
    async def test_create_note(self, async_client: AsyncClient, jwt_token: str):
        data_note = {
            "title": "title",
            "content": "content",
        }
        headers = {"Authorization": f"Bearer {jwt_token}"}
        response = await async_client.post("/notes/", json=data_note, headers=headers)
        assert response.status_code == 201

        created_note = response.json()
        assert "id" in created_note
        assert created_note["title"] == data_note["title"]
        assert created_note["content"] == data_note["content"]
        assert "created_at" in created_note
        assert "updated_at" in created_note

        async with async_session_maker() as session:
            query = select(Note).where(Note.id == created_note["id"])
            result = await session.execute(query)
            result = result.fetchone()
            assert result is not None
            note_db = result[0]
            assert note_db.user_id == 1

    async def test_create_note_unauthorized_user(self, async_client: AsyncClient):
        data_note = {
            "title": "title",
            "content": "content",
        }
        response = await async_client.post("/notes/", json=data_note)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    async def test_create_note_not_valid(
        self, async_client: AsyncClient, jwt_token: str
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}

        data_note_1 = {
            "content": "content",
        }
        response = await async_client.post("/notes/", json=data_note_1, headers=headers)
        assert response.status_code == 422
        assert "field required" in str(response.content)

        data_note_2 = {
            "title": "title",
        }
        response = await async_client.post("/notes/", json=data_note_2, headers=headers)
        assert response.status_code == 422
        assert "field required" in str(response.content)
