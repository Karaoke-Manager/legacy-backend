import pytest
from flask import Flask
from flask.testing import FlaskCliRunner
from flask_sqlalchemy import SQLAlchemy
from werkzeug import Client

import tests.data
from app import create_app
from karman.models import db as karman_db


@pytest.fixture(scope='function')
def app() -> Flask:
    """
    The test app with its config.
    """
    return create_app(extra_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })


@pytest.fixture(scope="function")
def cli(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def client(app: Flask) -> Client:
    """
    The test client used to send test requests to the APOS backend app.
    """
    context = app.app_context()
    context.push()
    yield app.test_client()
    context.pop()


@pytest.fixture(scope='function', autouse=True)
def db(client: Client) -> SQLAlchemy:
    """
    This fixture sets up the database for testing.
    :param client: The test client (we need to make sure that the client fixture runs first).
    """
    karman_db.create_all()
    yield karman_db
    karman_db.session.remove()
    karman_db.drop_all()


@pytest.fixture(scope='function')
def single_user_dataset(client: Client, db: SQLAlchemy):
    return tests.data.SingleUserDataset()


@pytest.fixture(scope='function')
def multi_user_dataset(client: Client, db: SQLAlchemy):
    return tests.data.MultiUserDataset()
