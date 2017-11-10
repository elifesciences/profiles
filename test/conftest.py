import logging
import os
from unittest.mock import MagicMock

from _pytest.fixtures import FixtureRequest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from pytest import fixture
from sqlalchemy.orm import scoped_session

from profiles.clients import Client, Clients
from profiles.config import CiConfig
from profiles.factory import create_app
from profiles.models import (
    Name,
    Profile,
    db
)

TEST_DATABASE_NAME = 'test.db'
TEST_DATABASE_PATH = os.path.dirname(os.path.realpath(__file__)) + '/../build/' + TEST_DATABASE_NAME
TEST_DATABASE_URI = 'sqlite:///' + TEST_DATABASE_PATH

logging.disable(logging.CRITICAL)


@fixture(scope='session')
def app(request: FixtureRequest) -> Flask:
    app = create_app(
        CiConfig(
            orcid={
                'api_uri': 'http://www.example.com/api',
                'authorize_uri': 'http://www.example.com/server/authorize',
                'token_uri': 'http://www.example.com/server/token',
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
            },
            db=TEST_DATABASE_URI,
            logging={},
            bus={
                'region': 'us-east-1',
                'subscriber': '1234567890',
                'name': 'bus-profiles'
            }
        ),
        clients=Clients(
            Client(name='client', client_id='client_id', client_secret='client_secret',
                   redirect_uri='http://www.example.com/client/redirect'),
        ),
    )

    ctx = app.app_context()
    ctx.push()

    def teardown() -> None:
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@fixture(scope='session', autouse=True)
def database(app: Flask, request: FixtureRequest) -> SQLAlchemy:
    if os.path.exists(TEST_DATABASE_PATH):
        os.unlink(TEST_DATABASE_PATH)

    db.app = app
    db.create_all()

    def teardown() -> None:
        db.drop_all()
        os.unlink(TEST_DATABASE_PATH)

    request.addfinalizer(teardown)
    return db


@fixture(scope='function', autouse=True)
def session(database: SQLAlchemy, request: FixtureRequest) -> scoped_session:
    connection = database.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = database.create_scoped_session(options=options)

    database.session = session

    def teardown() -> None:
        transaction.rollback()
        connection.close()
        session.remove()

    request.addfinalizer(teardown)
    return session


@fixture
def test_client(app: Flask) -> FlaskClient:
    return app.test_client()


@fixture
def mock_publisher() -> MagicMock:
    publisher = MagicMock()
    publisher.publish = MagicMock()
    return publisher


@fixture
def profile() -> Profile:
    return Profile('12345678', Name('foo'), '0001-0002-1825-0097')
