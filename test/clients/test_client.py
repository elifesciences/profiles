from hypothesis import given
from hypothesis.strategies import lists, one_of, text

from profiles.clients import Client


# TODO: aren't these overkill for a Value Object that is little more than a tuple?
@given(text(min_size=1), text(min_size=1), text(min_size=1), lists(one_of(["example.com", "example.org", "testing.example.org"]), min_size=1, max_size=3))
def test_it_can_be_printed(name, client_id, client_secret, redirect_uris):
    client = Client(name, client_id, client_secret, redirect_uris)

    assert '{!r}'.format(client) == "<Client {name!r}>".format(name=name)


@given(text(min_size=1), text(min_size=1), text(min_size=1), lists(one_of(["example.com", "example.org", "testing.example.org"]), min_size=1, max_size=3))
def test_it_has_a_name(name, client_id, client_secret, redirect_uris):
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.name == name


@given(text(min_size=1), text(min_size=1), text(min_size=1), lists(one_of(["example.com", "example.org", "testing.example.org"]), min_size=1, max_size=3))
def test_it_has_a_client_id(name, client_id, client_secret, redirect_uris):
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.client_id == client_id


@given(text(min_size=1), text(min_size=1), text(min_size=1), lists(one_of(["example.com", "example.org", "testing.example.org"]), min_size=1, max_size=3))
def test_it_has_a_client_secret(name, client_id, client_secret, redirect_uris):
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.client_secret == client_secret


@given(text(min_size=1), text(min_size=1), text(min_size=1), lists(one_of(["example.com", "example.org", "testing.example.org"]), min_size=1, max_size=3))
def test_it_has_redirect_uris(name, client_id, client_secret, redirect_uris):
    client = Client(name, client_id, client_secret, redirect_uris)

    assert client.redirect_uris == redirect_uris

