import os

import pytest
from fastapi import FastAPI
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

import karman
import tests.data
from karman import database
from karman.models import Model


@pytest.fixture(scope='function')
def app() -> FastAPI:
    """
    The test app with its config.
    """
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    return karman.app


@pytest.fixture(scope='function')
def client(app: FastAPI) -> TestClient:
    """
    The test client used to send test requests to the APOS backend app.
    """
    client = TestClient(app)
    return client


@pytest.fixture(scope='function', autouse=True)
def db(client: TestClient) -> Session:
    """
    This fixture sets up the database for testing.
    :param client: The test client (we need to make sure that the client fixture runs first).
    """
    Model.metadata.create_all()
    session = database.Session()
    yield session
    session.close()
    Model.metadata.drop_all()


@pytest.fixture(scope='function')
def single_user_dataset(client: TestClient, db: Session):
    return tests.data.SingleUserDataset().load(db)


@pytest.fixture(scope='function')
def multi_user_dataset(client: TestClient, db: Session):
    return tests.data.MultiUserDataset().load(db)
