import pytest
from requests import Response
from starlette import status
from starlette.testclient import TestClient


@pytest.mark.parametrize("method", ["get", "put", "patch", "head"])
def test_invalid_method(client: TestClient, method: str):
    response: Response = getattr(client, method)('/v1/login')
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_empty_request_body(client: TestClient):
    response: Response = client.post('/v1/login')
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
def test_incomplete_request_body(client: TestClient, data: dict):
    response: Response = client.post('/v1/login', data)
    assert response.status_code == 422
