from flask import Flask
from flask.testing import FlaskClient
from profiles.factory import create_app
from pytest import fixture


@fixture
def app() -> Flask:
    return create_app({
        'oauth2': {
            'clients': {
                'client': {
                    'id': 'client_id',
                    'secret': 'client_secret',
                    'redirect_uri': 'http://www.example.com/client/redirect'
                }
            },
            'server': {
                'authorize_uri': 'http://www.example.com/server/authorize',
                'token_uri': 'http://www.example.com/server/token',
                'client_id': 'server_client_id',
                'client_secret': 'server_client_secret',
            }
        }
    })


@fixture
def test_client(app: Flask) -> FlaskClient:
    return app.test_client()
