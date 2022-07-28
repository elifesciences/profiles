import hashlib
import logging
import os
from typing import Callable, Dict
from unittest.mock import MagicMock, patch

from _pytest.fixtures import FixtureRequest
from flask import Flask
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy, models_committed
from hypothesis import settings as hyp_settings
from hypothesis.configuration import set_hypothesis_home_dir
from hypothesis.database import DirectoryBasedExampleDatabase
from itsdangerous import URLSafeSerializer
from pytest import fixture
from sqlalchemy import event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session, scoped_session

from profiles.clients import Client, Clients
from profiles.config import DevConfig
from profiles.factory import create_app
from profiles.models import Date, Name, OrcidToken, Profile, db
from profiles.orcid import OrcidClient
from profiles.repositories import SQLAlchemyOrcidTokens, SQLAlchemyProfiles
from profiles.utilities import expires_at

BUILD_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/build/'

TEST_DATABASE_NAME = 'test.db'
TEST_DATABASE_PATH = BUILD_PATH + TEST_DATABASE_NAME
TEST_DATABASE_URI = 'sqlite:///' + TEST_DATABASE_PATH

logging.disable(logging.CRITICAL)

set_hypothesis_home_dir(BUILD_PATH + 'hypothesis/home')
# lsh@2022-07-27: 'database_file' removed in 4.x, replaced with this:
# - https://hypothesis.readthedocs.io/en/latest/database.html#upgrading-hypothesis-and-changing-your-tests
hyp_settings.register_profile('default', hyp_settings(database=DirectoryBasedExampleDatabase(BUILD_PATH + 'hypothesis/db')))
hyp_settings.load_profile('default')


@fixture(scope='session')
def app(request: FixtureRequest) -> Flask:
    app = create_app(
        DevConfig(
            orcid={
                'api_uri': 'http://www.example.com/api',
                'authorize_uri': 'http://www.example.com/oauth/authorize',
                'token_uri': 'http://www.example.com/oauth/token',
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
                'read_public_access_token': 'server_read_public_access_token',
                'webhook_access_token': 'server_webhook_access_token',
                'webhook_key': 'webhook_key',
            },
            db=TEST_DATABASE_URI,
            logging={},
            bus={
                'region': 'us-east-1',
                'subscriber': '1234567890',
                'name': 'bus-profiles'
            },
            server_name='localhost',
            scheme='http',
        ),
        clients=Clients(
            Client(name='client', client_id='client_id', client_secret='client_secret',
                   redirect_uris=['http://www.example.com/client/redirect']),
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

    # Bypass pysqlite's broken transactions (see https://bit.ly/2DKiixa).
    # pylint:disable=unused-argument
    # pylint:disable=unused-variable
    @event.listens_for(db.engine, 'connect')
    def do_connect(connection: Connection, *args) -> None:
        connection.isolation_level = None

    # pylint:disable=unused-variable
    @event.listens_for(db.engine, 'begin')
    def do_begin(connection: Connection) -> None:
        connection.execute('BEGIN')

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
def tomorrow():
    return Date.tomorrow()


@fixture
def mock_publisher() -> MagicMock:
    publisher = MagicMock()
    publisher.publish = MagicMock()
    return publisher


@fixture
def mock_orcid_client() -> MagicMock:
    client = MagicMock()
    client.remove_webhook = MagicMock()
    client.set_webhook = MagicMock()
    return client


@fixture
def orcid_client() -> OrcidClient:
    return OrcidClient('http://www.example.com/api')


@fixture
def orcid_config() -> Dict[str, str]:
    return {
        'api_uri': 'http://www.example.com/api',
        'authorize_uri': 'http://www.example.com/oauth/authorize',
        'token_uri': 'http://www.example.com/oauth/token',
        'client_id': 'server_client_id',
        'client_secret': 'server_client_secret',
        'read_public_access_token': 'server_read_public_access_token',
        'webhook_access_token': 'server_webhook_access_token',
        'webhook_key': 'webhook_key',
    }


@fixture
def orcid_token() -> OrcidToken:
    return OrcidToken('0000-0002-1825-0097', '1/fFAGRNJru1FTz70BzhT3Zg', expires_at(1234))


@fixture
def orcid_tokens() -> SQLAlchemyOrcidTokens:
    return SQLAlchemyOrcidTokens(db)


@fixture
def profiles() -> SQLAlchemyProfiles:
    return SQLAlchemyProfiles(db)


@fixture
def registered_handler_names():
    handler_names = []
    for id_, recv in models_committed.receivers.items():  # pylint:disable=unused-variable
        try:
            handler_names.append(recv.__name__)
        except AttributeError:
            pass
    return handler_names


@fixture()
def url_safe_serializer() -> URLSafeSerializer:
    return URLSafeSerializer('webhook_key', signer_kwargs={'key_derivation': 'hmac',
                                                           'digest_method': hashlib.sha512})


@fixture()
def webhook_payload(url_safe_serializer: URLSafeSerializer) -> str:
    return url_safe_serializer.dumps('0000-0002-1825-0097')


@fixture
def profile() -> Profile:
    return Profile('12345678', Name('foo'), '0000-0002-1825-0097')


@fixture
def yesterday():
    return Date.yesterday()


@fixture
def public_token_resp_data():
    return {"access_token": "4bed1e13-7792-4129-9f07-aaf7b88ba88f",
            "token_type": "bearer",
            "refresh_token": "2d76d8d0-6fd6-426b-a017-61e0ceda0ad2",
            "expires_in": 631138518,
            "scope": "/read-public",
            "orcid": None}


@fixture
def commit(session: Session) -> Callable[[], None]:
    def wrapped() -> None:
        with patch('profiles.orcid.request'):
            session.commit()

    return wrapped
