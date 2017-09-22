import pytest

from profiles.clients import Client, Clients


def test_it_contains_clients():
    client1 = Client('name1', 'client_id1', 'client_secret1', 'redirect_uri1')
    client2 = Client('name2', 'client_id2', 'client_secret2', 'redirect_uri2')
    clients = Clients(client1, client2)

    assert len(clients) == 2


def test_it_finds_clients():
    client1 = Client('name1', 'client_id1', 'client_secret1', 'redirect_uri1')
    client2 = Client('name2', 'client_id2', 'client_secret2', 'redirect_uri2')
    clients = Clients(client1, client2)

    assert len(clients) == 2

    assert clients.find('client_id1') == client1
    assert clients.find('client_id2') == client2

    with pytest.raises(KeyError):
        clients.find('client_id3')
