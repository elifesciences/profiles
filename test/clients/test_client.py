from profiles.clients import Client


name = 'journal'
client_id = 'client_id'
client_secret = 'client_secret'
redirect_uris = ['example.com', 'example.org', 'testing.example.org']


def test_it_can_be_printed():
    client = Client(name, client_id, client_secret, redirect_uris)

    assert '{!r}'.format(client) == "<Client {name!r}>".format(name=name)


def test_it_has_a_name():
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.name == name


def test_it_has_a_client_id():
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.client_id == client_id


def test_it_has_a_client_secret():
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.client_secret == client_secret


def test_it_has_redirect_uris():
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.redirect_uris == redirect_uris

def test_it_must_have_at_least_one_redirect_uri():
    with pytest.raises(ValueError):
        client = Client(name, client_id, client_secret, [])

def test_it_has_a_canonical_redirect_uri():
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.canonical_redirect_uri == 'example.com'
