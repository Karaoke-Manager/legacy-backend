import pytest
from httpx import AsyncClient, Response
from starlette import status

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("method", ["get", "put", "patch", "head"])
async def test_invalid_method(client: AsyncClient, method: str):
    response: Response = await getattr(client, method)('/v1/login')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


async def test_empty_request_body(client: AsyncClient):
    response = await client.post('/v1/login')
    assert response.status_code == 422


@pytest.mark.parametrize("data", [
    {},
    {"username": ""},
    {"password": ""},
    {"username": "", "password": ""},
    {"username": "name"},
    {"username": "name", "password": ""},
    {"username": "", "password": "pass"},
])
@pytest.mark.usefixtures("dataset")
async def test_incomplete_request_body(client: AsyncClient, data: dict):
    response = await client.post('/v1/login', data=data)
    assert response.status_code == 422
