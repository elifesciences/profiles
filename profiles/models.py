from datetime import datetime
from typing import Any, Iterable

import pendulum
from sqlalchemy.orm import composite

from profiles.database import UTCDateTime, db

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
    def __init__(self, given_names: str, family_name: str = None) -> None:
        self.given_names = given_names
        self.family_name = family_name

    def __composite_values__(self) -> Iterable[str]:
        return self.given_names, self.family_name

    def __str__(self) -> str:
        if self.family_name is None:
            return self.given_names

        return '%s %s' % (self.given_names, self.family_name)

    def __repr__(self) -> str:
        return '<Name %r %r>' % (self.given_names, self.family_name)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Name) and \
               other.given_names == self.given_names and \
               other.family_name == self.family_name

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class Profile(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True)
    name = composite(Name, '_given_names', '_family_name')
    _given_names = db.Column(db.Text(), name='given_names', nullable=False)
    _family_name = db.Column(db.Text(), name='family_name')
    orcid = db.Column(db.String(19), unique=True)

    def __init__(self, profile_id: str, name: Name, orcid: str = None) -> None:
        self.id = profile_id
        self.name = name
        self.orcid = orcid

    def __repr__(self) -> str:
        return '<Profile %r>' % self.id
