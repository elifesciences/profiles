from profiles.clients import Client


def test_it_can_be_printed():
    client = Client('name', 'client_id', 'client_secret', 'redirect_uri')

    assert repr(client) == "<Client 'name'>"


def test_it_has_a_name():
    client = Client('name', 'client_id', 'client_secret', 'redirect_uri')

    assert client.name == 'name'


def test_it_has_a_client_id():
    client = Client('name', 'client_id', 'client_secret', 'redirect_uri')

    assert client.client_id == 'client_id'


def test_it_has_a_client_secret():
    client = Client('name', 'client_id', 'client_secret', 'redirect_uri')

    assert client.client_secret == 'client_secret'


def test_it_has_a_redirect_uri():
    client = Client('name', 'client_id', 'client_secret', 'redirect_uri')

    assert client.redirect_uri == 'redirect_uri'
