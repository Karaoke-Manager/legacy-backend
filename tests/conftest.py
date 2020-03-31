import pytest
from requests import Response
from sqlalchemy import orm
from starlette.testclient import TestClient

from data import Dataset
from karman import models, app
from karman.config import app_config
from karman.utils import db_engine, Session


@pytest.fixture(scope='function', autouse=True)
def db() -> orm.Session:
    app_config.database = app_config.test.database
    app_config.redis = app_config.test.redis
    models.Model.metadata.create_all(db_engine)
    session = Session()
    yield session
    session.close()
    models.Model.metadata.drop_all(db_engine)


@pytest.fixture(scope='function')
def client() -> TestClient:
    client = TestClient(app)
    return client


@pytest.fixture(scope='function')
def dataset(client: TestClient, db: orm.Session) -> Dataset:
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
