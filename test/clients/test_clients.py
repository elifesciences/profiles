from hypothesis import given
from hypothesis.searchstrategy.lazy import LazyStrategy
from hypothesis.strategies import lists, text
import pytest
from profiles.clients import Client, Clients


def list_of_str(length: int) -> LazyStrategy:
    return lists(text(), max_size=length, min_size=length)


@given(list_of_str(4), list_of_str(4))
def test_it_contains_clients(client1_args, client2_args):
    clients = Clients(Client(*client1_args), Client(*client2_args))

    assert len(clients) == 2


@given(text(min_size=1))
def test_it_finds_clients(id_base):
    client_id1 = id_base + '1'
    client_id2 = id_base + '2'
    unknown_client_id = id_base + 'unkwown'

    client1 = Client('name1', client_id1, 'client_secret1', 'redirect_uri1')
    client2 = Client('name2', client_id2, 'client_secret2', 'redirect_uri2')
    clients = Clients(client1, client2)

    assert len(clients) == 2

    assert clients.find(client_id1) == client1
    assert clients.find(client_id2) == client2

    with pytest.raises(KeyError):
        clients.find(unknown_client_id)
