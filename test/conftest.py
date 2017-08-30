from profiles import create_app
from pytest import fixture


@fixture
def app():
    return create_app()


@fixture
def test_client(app):
    return app.test_client()
