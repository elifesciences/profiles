import collections
from typing import Any, Iterable


class Client(object):
    def __init__(self, name: str, client_id: str, client_secret: str, redirect_uri: str) -> None:
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def __repr__(self) -> str:
        return '<Client %r>' % self.name


class Clients(collections.Set):
    def __init__(self, *args: Client) -> None:
        self.elements = []
        for value in args:
            if value not in self.elements:
                self.elements.append(value)

    def find(self, client_id: str) -> Client:
        try:
            return next(v for v in self.elements if v.client_id == client_id)
        except StopIteration as exception:
            raise KeyError('No client with the client_id') from exception

    def __iter__(self) -> Iterable:
        return iter(self.elements)

    def __contains__(self, value: Any) -> bool:
        return value in self.elements

    def __len__(self) -> int:
        return len(self.elements)
