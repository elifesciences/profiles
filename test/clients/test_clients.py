from hypothesis import given
from hypothesis.strategies import text

import pytest

from profiles.clients import Client, Clients


def test_it_contains_clients():
    clients = Clients(
        Client('name1', 'client_id1', 'client_secret1', ['redirect_uri1']),
        Client('name2', 'client_id2', 'client_secret2', ['redirect_uri2'])
    )

    assert len(clients) == 2


@given(text(min_size=1))
def test_it_finds_clients(id_base):
    client_id1 = id_base + '1'
    client_id2 = id_base + '2'
    unknown_client_id = id_base + 'unknown'

    client1 = Client('name1', client_id1, 'client_secret1', ['redirect_uri1'])
    client2 = Client('name2', client_id2, 'client_secret2', ['redirect_uri2'])
    clients = Clients(client1, client2)

    assert len(clients) == 2

    assert clients.find(client_id1) == client1
    assert clients.find(client_id2) == client2

    for client in clients:
        assert isinstance(client, Client)
        assert client in clients

    with pytest.raises(KeyError):
        clients.find(unknown_client_id)
