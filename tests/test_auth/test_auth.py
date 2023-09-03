import json

from httpx import AsyncClient, Client

from tests.test_auth.conftest import get_user_from_database


# Асинхронный тест
async def test_register_ac(async_client: AsyncClient):
    data_user = {
      'email': 'user@example.com',
      'password': 'string',
      'user_name': 'user_name',
    }
    data_user_db = {
        'id': 1,
        'email': 'user@example.com',
        'is_active': True,
        'is_superuser': False,
        'is_verified': False,
        'user_name': 'user_name',
    }

    response = await async_client.post('/auth/register', json=data_user)
    data_from_response = response.json()

    assert response.status_code == 201
    assert data_from_response == data_user_db

    users_from_db = await get_user_from_database(data_from_response['id'])
    assert data_user_db['id'] == users_from_db.id
    assert data_user_db['email'] == users_from_db.email
    assert data_user_db['user_name'] == users_from_db.user_name


# Синхронный тест
def test_registering_an_existing_user(client: Client):
    data_user = {
        'email': 'user@example.com',
        'password': 'string',
        'user_name': 'user_name',
    }
    response = client.post('/auth/register', json=data_user)
    assert response.status_code == 400
    assert response.json()['detail'] == 'REGISTER_USER_ALREADY_EXISTS'


async def test_login(async_client: AsyncClient):
    data_user = {
        'username': 'user@example.com',
        'password': 'string',
    }
    response = await async_client.post('/auth/jwt/login', data=data_user)
    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'token_type' in response.json()
