from hypothesis import given
from hypothesis.strategies import text
from profiles.clients import Client


@given(text(min_size=1), text(min_size=1), text(min_size=1), text(min_size=1))
def test_it_can_be_printed(name, client_id, client_secret, redirect_uri):
    client = Client(name, client_id, client_secret, redirect_uri)

    assert '{!r}'.format(client) == "<Client {name!r}>".format(name=name)


@given(text(min_size=1), text(min_size=1), text(min_size=1), text(min_size=1))
def test_it_has_a_name(name, client_id, client_secret, redirect_uri):
    client = Client(name, client_id, client_secret, redirect_uri)

    assert client.name == name


@given(text(min_size=1), text(min_size=1), text(min_size=1), text(min_size=1))
def test_it_has_a_client_id(name, client_id, client_secret, redirect_uri):
    client = Client(name, client_id, client_secret, redirect_uri)

    assert client.client_id == client_id


@given(text(min_size=1), text(min_size=1), text(min_size=1), text(min_size=1))
def test_it_has_a_client_secret(name, client_id, client_secret, redirect_uri):
    client = Client(name, client_id, client_secret, redirect_uri)

    assert client.client_secret == client_secret


@given(text(min_size=1), text(min_size=1), text(min_size=1), text(min_size=1))
def test_it_has_a_redirect_uri(name, client_id, client_secret, redirect_uri):
    client = Client(name, client_id, client_secret, redirect_uri)

    assert client.redirect_uri == redirect_uri
