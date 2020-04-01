import pytest
from httpx import AsyncClient, Response
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.status import *

from data import Dataset
from karman import schemas, models
from karman.scopes import all_scopes

pytestmark = pytest.mark.asyncio


def equal_roles(schema, db):
    return schemas.Role(**schema) == schemas.Role.from_orm(db)


async def test_list_roles_unauthenticated(client: AsyncClient):
    response = await client.get("/v1/roles/")
    assert response.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("method", ["put", "patch", "delete"])
@pytest.mark.usefixtures("login:admin")
async def test_invalid_roles_methods(client: AsyncClient, method: str):
    response: Response = await getattr(client, method)("/v1/roles/")
    assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.usefixtures("login:admin")
async def test_list_roles(client: AsyncClient, dataset: Dataset):
    response = await client.get("/v1/roles/")
    assert response.status_code == HTTP_200_OK
    assert equal_roles(response.json()[0], dataset.manager_role)


@pytest.mark.usefixtures("login:admin")
async def test_get_role(client: AsyncClient, dataset: Dataset):
    response = await client.get(f"/v1/roles/{dataset.manager_role.id}/")
    assert equal_roles(response.json(), dataset.manager_role)


@pytest.mark.usefixtures("login:admin")
async def test_update_role_id(client: AsyncClient, dataset: Dataset):
    response = await client.put(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id + 1,
        "name": dataset.manager_role.name,
        "scopes": list(dataset.manager_role.scopes)
    })
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("login:admin")
async def test_update_role_name(client: AsyncClient, db: AsyncIOMotorDatabase, dataset: Dataset):
    response = await client.put(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id,
        "name": dataset.UNUSED_ROLE,
        "scopes": list(dataset.manager_role.scopes)
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert schemas.Role(**response.json()).name == dataset.UNUSED_ROLE
    assert dataset.manager_role.name == dataset.UNUSED_ROLE


@pytest.mark.usefixtures("login:admin")
async def test_update_role_scopes(client: AsyncClient, db: AsyncIOMotorDatabase, dataset: Dataset):
    response = await client.put(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id,
        "name": dataset.manager_role.name,
        "scopes": list(all_scopes.keys())
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert schemas.Role(**response.json()).scopes == all_scopes.keys()


@pytest.mark.usefixtures("login:admin")
async def test_patch_role_id(client: AsyncClient, db: AsyncIOMotorDatabase, dataset: Dataset):
    response = await client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "id": dataset.manager_role.id + 1
    })
    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.usefixtures("login:admin")
async def test_patch_role_name(client: AsyncClient, db: AsyncIOMotorDatabase, dataset: Dataset):
    response = await client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "name": dataset.UNUSED_ROLE
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert dataset.manager_role.name == dataset.UNUSED_ROLE
    assert len(dataset.manager_role.scopes) > 0


@pytest.mark.usefixtures("login:admin")
async def test_patch_role_scopes(client: AsyncClient, db: AsyncIOMotorDatabase, dataset: Dataset):
    previous_name = dataset.manager_role.name
    response = await client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "scopes": list(all_scopes.keys())
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert dataset.manager_role.name == previous_name
    assert dataset.manager_role.scopes == all_scopes.keys()


@pytest.mark.usefixtures("login:admin")
async def test_patch_role_name_and_scopes(client: AsyncClient, db: AsyncIOMotorDatabase, dataset: Dataset):
    response = await client.patch(f"/v1/roles/{dataset.manager_role.id}", json={
        "name": dataset.UNUSED_ROLE,
        "scopes": list(all_scopes.keys())
    })
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert dataset.manager_role.name == dataset.UNUSED_ROLE
    assert dataset.manager_role.scopes == all_scopes.keys()


@pytest.mark.usefixtures("login:admin")
async def test_delete_role(client: AsyncClient, db: AsyncIOMotorDatabase, dataset: Dataset):
    schema = schemas.Role.from_orm(dataset.manager_role)
    response = await client.delete(f"/v1/roles/{dataset.manager_role.id}")
    db.expire(dataset.manager_role)
    assert response.status_code == HTTP_200_OK
    assert schemas.Role(**response.json()) == schema
    assert db.query(models.Role).get(schema.id) is None
