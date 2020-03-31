import pytest
from requests import Response
from sqlalchemy.orm import Session
from starlette.status import *
from starlette.testclient import TestClient

from data import Dataset
from karman import schemas, all_scopes, models


def equal_roles(schema, db):
    return schemas.Role(**schema) == schemas.Role.from_orm(db)


def test_list_roles_unauthenticated(client: TestClient):
    response: Response = client.get("/v1/roles/")
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
@pytest.mark.usefixtures("login:admin")
def test_invalid_roles_methods(client: TestClient, method: str):
    response: Response = getattr(client, method)("/v1/roles/")
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.usefixtures("login:admin")
def test_list_roles(client: TestClient, dataset: Dataset):
    response: Response = client.get("/v1/roles/")
    assert response.status_code == HTTP_200_OK
    assert equal_roles(response.json()[0], dataset.manager_role)


@pytest.mark.usefixtures("login:admin")
def test_get_role(client: TestClient, dataset: Dataset):
    response: Response = client.get(f"/v1/roles/{dataset.manager_role.id}/")
    assert equal_roles(response.json(), dataset.manager_role)


@pytest.mark.usefixtures("login:admin")
def test_update_role_id(client: TestClient, dataset: Dataset):
    response: Response = client.put(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id + 1,
        "name": dataset.manager_role.name,
        "scopes": list(dataset.manager_role.scopes)
    })
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("login:admin")
def test_update_role_name(client: TestClient, db: Session, dataset: Dataset):
    response: Response = client.put(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id,
        "name": dataset.UNUSED_ROLE,
        "scopes": list(dataset.manager_role.scopes)
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert schemas.Role(**response.json()).name == dataset.UNUSED_ROLE
    assert dataset.manager_role.name == dataset.UNUSED_ROLE


@pytest.mark.usefixtures("login:admin")
def test_update_role_scopes(client: TestClient, db: Session, dataset: Dataset):
    response: Response = client.put(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id,
        "name": dataset.manager_role.name,
        "scopes": list(all_scopes.keys())
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert schemas.Role(**response.json()).scopes == all_scopes.keys()


@pytest.mark.usefixtures("login:admin")
def test_patch_role_id(client: TestClient, db: Session, dataset: Dataset):
    response: Response = client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id + 1
    })
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("login:admin")
def test_patch_role_name(client: TestClient, db: Session, dataset: Dataset):
    response: Response = client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "name": dataset.UNUSED_ROLE
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert dataset.manager_role.name == dataset.UNUSED_ROLE
    assert len(dataset.manager_role.scopes) > 0


@pytest.mark.usefixtures("login:admin")
def test_patch_role_scopes(client: TestClient, db: Session, dataset: Dataset):
    previous_name = dataset.manager_role.name
    response: Response = client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "scopes": list(all_scopes.keys())
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert dataset.manager_role.name == previous_name
    assert dataset.manager_role.scopes == all_scopes.keys()


@pytest.mark.usefixtures("login:admin")
def test_patch_role_name_and_scopes(client: TestClient, db: Session, dataset: Dataset):
    response: Response = client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "name": dataset.UNUSED_ROLE,
        "scopes": list(all_scopes.keys())
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert dataset.manager_role.name == dataset.UNUSED_ROLE
    assert dataset.manager_role.scopes == all_scopes.keys()


@pytest.mark.usefixtures("login:admin")
def test_delete_role(client: TestClient, db: Session, dataset: Dataset):
    schema = schemas.Role.from_orm(dataset.manager_role)
    response = client.delete(f"/v1/roles/{dataset.manager_role.id}")
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert schemas.Role(**response.json()) == schema
    assert db.query(models.Role).get(schema.id) is None
