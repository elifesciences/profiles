from flask import Flask
from flask.testing import FlaskClient
from profiles.factory import create_app
from pytest import fixture


@fixture
def app() -> Flask:
    return create_app()


@fixture
def test_client(app: Flask) -> FlaskClient:
    return app.test_client()
