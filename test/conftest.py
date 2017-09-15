from flask import Flask
from flask.testing import FlaskClient
from pytest import fixture

from profiles.clients import Client, Clients
from profiles.config import CiConfig
from profiles.factory import create_app


@fixture
def app() -> Flask:
    return create_app(
        CiConfig(
            orcid={
                'authorize_uri': 'http://www.example.com/server/authorize',
                'token_uri': 'http://www.example.com/server/token',
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
            },
        ),
        clients=Clients([
            Client(name='client', client_id='client_id', client_secret='client_secret',
                   redirect_uri='http://www.example.com/client/redirect'),
        ]),
    )


@fixture
def test_client(app: Flask) -> FlaskClient:
    return app.test_client()
