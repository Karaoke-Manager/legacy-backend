import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug import Client

from app import create_app
from karman import db


@pytest.fixture(scope='function')
def app() -> Flask:
    """
    The test app with its config.
    """
    return create_app(extra_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })


@pytest.fixture(scope='function')
def client(app) -> Client:
    """
    The test client used to send test requests to the APOS backend app.
    """
    context = app.app_context()
    context.push()
    yield app.test_client()
    context.pop()


@pytest.fixture(scope='function', autouse=True)
def database(client) -> SQLAlchemy:
    """
    This fixture sets up the database for testing.
    :param client: The test client (we need to make sure that the client fixture runs first).
    """
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()
