from httpx import AsyncClient
from sqlalchemy import Delete, Insert, Select

from note_app.models import Note
from tests.conftest import async_session_maker


class TestCreateNote:
    async def test_create_note(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
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
            query = Select(Note).where(Note.id == created_note["id"])
            result = await session.execute(query)
            result = result.fetchone()

        assert result is not None
        note_db = result[0]
        assert note_db.user_id == 1

        async with async_session_maker() as session:
            query = Delete(Note).where(Note.id == created_note["id"])
            await session.execute(query)
            await session.commit()

    async def test_create_note_unauthorized_user(self, async_client: AsyncClient):
        data_note = {
            "title": "title",
            "content": "content",
        }
        response = await async_client.post("/notes/", json=data_note)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    async def test_create_note_not_valid(
        self,
        async_client: AsyncClient,
        jwt_token: str,
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


class TestDeleteNote:
    async def test_delete_note(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}
        test_note = {
            "title": "test_delete_title",
            "content": "test_delete_content",
            "user_id": 1,
        }
        async with async_session_maker() as session:
            query = Insert(Note).values(test_note).returning(Note.id)
            result = await session.execute(query)
            await session.commit()
        note_id = result.scalar()
        response = await async_client.delete(f"/notes/{note_id}/", headers=headers)
        assert response.status_code == 200
        assert response.json() == f"Объект с идентификатором {note_id} успешно удален"

    async def test_delete_non_existent_note(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}
        note_id = 1000
        response = await async_client.delete(f"/notes/{note_id}/", headers=headers)
        assert response.status_code == 404
        assert (
            response.json()["detail"] == f"Объект с идентификатором {note_id} не найден"
        )

    async def test_delete_note_unauthorized_user(self, async_client: AsyncClient):
        note_id = 1
        response = await async_client.delete(f"/notes/{note_id}/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

        async with async_session_maker() as session:
            query = Select(Note.id).where(Note.id == note_id)
            result = await session.execute(query)
        assert result.scalar()

    async def test_delete_note_non_permission_user(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}

        async with async_session_maker() as session:
            query = Select(Note.id).where(Note.user_id == 2)
            result = await session.execute(query)
        note_id = result.scalar()

        response = await async_client.delete(f"/notes/{note_id}/", headers=headers)
        assert response.status_code == 403
        assert response.json()["detail"] == "Отсутствуют права на удаление объекта"

        async with async_session_maker() as session:
            query = Select(Note.id).where(Note.id == note_id)
            result = await session.execute(query)
        assert result.scalar()


class TestGetNote:
    async def test_get_note_bu_id(
        self,
        async_client: AsyncClient,
        test_notes: list[dict],
    ):
        note_id = 1
        response = await async_client.get(f"/notes/{note_id}/")
        assert response.status_code == 200

        note = response.json()
        assert note["id"] == note_id
        assert note["title"] == test_notes[0]["title"]
        assert note["content"] == test_notes[0]["content"]
        assert "created_at" in note
        assert "updated_at" in note

    async def test_get_non_existent_note_by_id(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        note_id = 1000
        response = await async_client.get(f"/notes/{note_id}/")
        assert response.status_code == 404
        assert (
            response.json()["detail"] == f"Объект с идентификатором {note_id} не найден"
        )

    async def test_get_notes(
        self,
        async_client: AsyncClient,
        test_notes: list[dict],
    ):
        response = await async_client.get("/notes/")
        assert response.status_code == 200

        notes = response.json()

        assert len(notes) == 25

        note = notes[-1]
        assert note["id"] == 5
        assert note["title"] == test_notes[4]["title"]
        assert note["content"] == test_notes[4]["content"]
        assert note["user_name"] == "test_user_1"
        assert "created_at" in note
        assert "updated_at" in note

    async def test_get_notes_pagination(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.get("/notes/?limit=20&page=1")
        assert response.status_code == 200
        assert len(response.json()) == 20

        response = await async_client.get("/notes/?limit=20&page=2")
        assert response.status_code == 200
        assert len(response.json()) == 10

    async def test_get_notes_sorted(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.get("/notes/?order_by=+title")
        assert response.status_code == 200
        assert response.json()[0]["title"] == "test_title_0"
        assert response.json()[1]["title"] == "test_title_1"
        assert response.json()[2]["title"] == "test_title_10"

        response = await async_client.get("/notes/?order_by=-title")
        assert response.status_code == 200
        assert response.json()[0]["title"] == "test_title_9"
        assert response.json()[1]["title"] == "test_title_8"
        assert response.json()[2]["title"] == "test_title_7"

        response = await async_client.get("/notes/?order_by=test,-test2")
        assert response.status_code == 422
        assert (
            response.json()["detail"] == "Переданы не корректные данные для сортировки"
        )

    async def test_get_notes_search(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.get("/notes/?search=le_9")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "test_title_9"

        response = await async_client.get("/notes/?search=tent_12")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["content"] == "test_content_12"

    async def test_get_notes_filters(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.get("/notes/?title=test_title_1")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["title"] == "test_title_1"

        response = await async_client.get("/notes/?user=t_user_2")
        assert response.status_code == 200
        assert len(response.json()) == 15
        assert response.json()[0]["user_name"] == "test_user_2"

    async def test_get_notes_user(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}

        response = await async_client.get("/notes/user/", headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        note = response_data[0]
        assert len(response_data) == 15
        assert response_data[0]
        assert note["id"] == 1
        assert note["title"] == "test_title_0"
        assert note["content"] == "test_content_0"
        assert "created_at" in note
        assert "updated_at" in note

    async def test_get_notes_unauthorized_user(
        self,
        async_client: AsyncClient,
    ):
        response = await async_client.get("/notes/user/")
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"


class TestUpdateNote:
    async def test_update_note(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}
        new_date_note = {
            "title": "test_title_new",
            "content": "test_content_new",
        }
        note_id = 1
        response = await async_client.put(
            f"/notes/{note_id}/",
            json=new_date_note,
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json() == f"Объект с идентификатором {note_id} успешно обновлен"
        async with async_session_maker() as session:
            query = Select(Note).where(Note.id == note_id)
            result = await session.execute(query)
            note = result.scalar()
        assert note.title == new_date_note["title"]
        assert note.content == new_date_note["content"]
        assert note.created_at != note.updated_at

        new_date_note_2 = {
            "title": "test_title_new_2",
        }
        response = await async_client.put(
            f"/notes/{note_id}/",
            json=new_date_note_2,
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json() == f"Объект с идентификатором {note_id} успешно обновлен"
        async with async_session_maker() as session:
            query = Select(Note).where(Note.id == note_id)
            result = await session.execute(query)
            note = result.scalar()
        assert note.title == new_date_note_2["title"]
        assert note.content == new_date_note["content"]

        new_date_note_3 = {
            "content": "test_content_new_3",
        }
        response = await async_client.put(
            f"/notes/{note_id}/",
            json=new_date_note_3,
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json() == f"Объект с идентификатором {note_id} успешно обновлен"
        async with async_session_maker() as session:
            query = Select(Note).where(Note.id == note_id)
            result = await session.execute(query)
            note = result.scalar()
        assert note.title == new_date_note_2["title"]
        assert note.content == new_date_note_3["content"]

    async def test_update_note_non_params(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}
        note_id = 1
        response = await async_client.put(
            f"/notes/{note_id}/", json={}, headers=headers
        )
        assert response.status_code == 400
        assert (
            response.json()["detail"] == "Не переданы параметры для обновления объекта"
        )

    async def test_update_non_existent_note(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}
        new_date_note = {
            "title": "test_title_new",
            "content": "test_content_new",
        }
        note_id = 1000
        response = await async_client.put(
            f"/notes/{note_id}/",
            json=new_date_note,
            headers=headers,
        )
        assert response.status_code == 404
        assert (
            response.json()["detail"] == f"Объект с идентификатором {note_id} не найден"
        )

    async def test_update_note_unauthorized_user(self, async_client: AsyncClient):
        note_id = 1000
        new_date_note = {
            "title": "test_title_new",
            "content": "test_content_new",
        }
        response = await async_client.put(f"/notes/{note_id}/", json=new_date_note)
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    async def test_update_note_non_permission_user(
        self,
        async_client: AsyncClient,
        jwt_token: str,
    ):
        headers = {"Authorization": f"Bearer {jwt_token}"}
        new_date_note = {
            "title": "test_title_new",
            "content": "test_content_new",
        }
        async with async_session_maker() as session:
            query = Select(Note).where(Note.user_id == 2)
            result = await session.execute(query)
        note_old = result.scalar()

        response = await async_client.put(
            f"/notes/{note_old.id}/", json=new_date_note, headers=headers
        )
        assert response.status_code == 403
        assert (
            response.json()["detail"] == "Отсутствуют права на редактирование объекта"
        )
        async with async_session_maker() as session:
            query = Select(Note).where(Note.id == note_old.id)
            result = await session.execute(query)
        note_new = result.scalar()
        assert note_old.title == note_new.title
        assert note_old.content == note_new.content
