from datetime import datetime
from typing import Any, Iterable

import pendulum
from sqlalchemy.orm import composite

from profiles.database import UTCDateTime, db
from profiles.utilities import guess_index_name

ID_LENGTH = 8


class OrcidToken(db.Model):
    orcid = db.Column(db.String(19), primary_key=True)
    access_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(UTCDateTime, nullable=False)

    def __init__(self, orcid: str, access_token: str, expires_at: datetime) -> None:
        self.orcid = orcid
        self.access_token = access_token
        self.expires_at = pendulum.timezone('utc').convert(expires_at)

    def __repr__(self) -> str:
        return '<OrcidToken for %r>' % self.orcid


class Name(object):
    def __init__(self, preferred: str, index: str = None) -> None:
        if index is None:
            index = guess_index_name(preferred)

        self.preferred = preferred
        self.index = index

    def __composite_values__(self) -> Iterable[str]:
        return self.preferred, self.index

    def __str__(self) -> str:
        return self.preferred

    def __repr__(self) -> str:
        return '<Name %r>' % self.preferred

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Name) and \
               other.preferred == self.preferred and \
               other.index == self.index

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class Profile(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True)
    name = composite(Name, '_preferred_name', '_index_name')
    _preferred_name = db.Column(db.Text(), name='preferred_name', nullable=False)
    _index_name = db.Column(db.Text(), name='index_name', nullable=False)
    orcid = db.Column(db.String(19), unique=True)

    def __init__(self, profile_id: str, name: Name, orcid: str = None) -> None:
        self.id = profile_id
        self.name = name
        self.orcid = orcid

    def __repr__(self) -> str:
        return '<Profile %r>' % self.id
