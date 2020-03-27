import pytest
from requests import Response
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

import karman
from karman import models
from karman.database import get_db_engine, make_session
from tests.data import Dataset


@pytest.fixture(scope='function')
def client() -> TestClient:
    client = TestClient(karman.app)
    return client


@pytest.fixture(scope='function', autouse=True)
def db() -> Session:
    models.Model.metadata.bind = get_db_engine(poolclass=StaticPool)
    models.Model.metadata.create_all()
    session = make_session()
    yield session
    session.close()
    models.Model.metadata.drop_all()


@pytest.fixture(scope='function')
def dataset(client: TestClient, db: Session) -> Dataset:
    dataset = Dataset()
    dataset.load(db)
    return dataset


@pytest.fixture(name="login:admin", scope="function")
def login_admin(client: TestClient, dataset: Dataset):
    response: Response = client.post("/v1/login", data={
        "username": dataset.admin.username,
        "password": dataset.ADMIN_PASSWORD
    })
    client.headers["Authorization"] = f"Bearer {response.json()['accessToken']}"
