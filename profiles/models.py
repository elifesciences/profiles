from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

from iso3166 import Country
import pendulum
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import composite

from profiles.database import ISO3166Country, UTCDateTime, db
from profiles.exceptions import AffiliationNotFound
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


class Address(object):
    def __init__(self, country: Country, city: str, region: str = None) -> None:
        self.city = city
        self.region = region
        self.country = country

    def __composite_values__(self) -> Iterable[Optional[str]]:
        return self.country, self.city, self.region

    def get_formatted(self) -> List[str]:
        return [self.city, self.region, self.country.alpha2]

    def get_components(self) -> Dict:
        return {
            "locality": [self.city],
            "area": [self.region],
            "country": self.country.name
        }

    def __repr__(self) -> str:
        return '<Address %r %r %r>' % (self.city, self.region, self.country.alpha2)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Address) and \
               other.city == self.city and \
               other.region == self.region and \
               other.country == self.country

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)


class Affiliation(db.Model):
    id = db.Column(db.Text(), primary_key=True)
    department = db.Column(db.Text())
    organisation = db.Column(db.Text(), nullable=False)
    address = composite(Address, '_country', '_city', '_region')
    _city = db.Column(db.Text(), name='city', nullable=False)
    _region = db.Column(db.Text(), name='region')
    _country = db.Column(ISO3166Country, name='country', nullable=False)
    starts = db.Column(UTCDateTime, nullable=False)
    ends = db.Column(UTCDateTime)
    restricted = db.Column(db.Boolean(), nullable=False)
    profile_id = db.Column(db.String(ID_LENGTH), db.ForeignKey('profile.id'))
    profile = db.relationship('Profile', back_populates='affiliations')
    position = db.Column(db.Integer())

    # pylint: disable=too-many-arguments
    def __init__(self, affiliation_id: str, address: Address, organisation: str, starts: datetime,
                 department: str = None, ends: datetime = None, restricted: bool = False) -> None:
        self.id = affiliation_id
        self.department = department
        self.organisation = organisation
        self.address = address
        self.starts = pendulum.timezone('utc').convert(starts)
        self.ends = pendulum.timezone('utc').convert(ends) if ends else None
        self.restricted = restricted

    def get_name_list(self) -> List[str]:
        return [self.department, self.organisation]

    def is_current(self) -> bool:
        starts = pendulum.instance(self.starts)
        ends = pendulum.instance(self.ends) if self.ends else None

        return starts.is_past() and (not ends or ends.is_future())

    def __repr__(self) -> str:
        return '<Affiliation %r>' % self.id


class Profile(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True)
    name = composite(Name, '_preferred_name', '_index_name')
    _preferred_name = db.Column(db.Text(), name='preferred_name', nullable=False)
    _index_name = db.Column(db.Text(), name='index_name', nullable=False)
    orcid = db.Column(db.String(19), unique=True)
    affiliations = db.relationship('Affiliation', order_by='Affiliation.position',
                                   collection_class=ordering_list('position'),
                                   cascade='all, delete-orphan', back_populates='profile')
    email_addresses = db.relationship('EmailAddress', order_by='EmailAddress.position',
                                      collection_class=ordering_list('position'),
                                      cascade='all, delete-orphan', back_populates='profile')

    def __init__(self, profile_id: str, name: Name, orcid: str = None) -> None:
        self.id = profile_id
        self.name = name
        self.orcid = orcid

    def add_affiliation(self, affiliation: Affiliation, position: int = 0) -> None:
        for existing_affiliation in self.affiliations:
            if existing_affiliation.id == affiliation.id:
                existing_affiliation.department = affiliation.department
                existing_affiliation.organisation = affiliation.organisation
                existing_affiliation.address = affiliation.address
                existing_affiliation.starts = affiliation.starts
                existing_affiliation.ends = affiliation.ends
                existing_affiliation.restricted = affiliation.restricted
                if position != existing_affiliation.position:
                    self.affiliations.remove(existing_affiliation)
                    self.affiliations.insert(position, existing_affiliation)
                    self.affiliations.reorder()
                return

        self.affiliations.insert(position, affiliation)
        self.affiliations.reorder()

    def get_affiliation(self, affiliation_id: str) -> Affiliation:
        for affiliation in self.affiliations:
            if affiliation.id == affiliation_id:
                return affiliation

        raise AffiliationNotFound('Affiliation with the ID {} not found'.format(id))

    def get_affiliations(self, current_only: bool = True) -> List[Affiliation]:
        if current_only:
            return sorted([aff for aff in self.affiliations if aff.is_current()],
                          key=lambda k: k.position)

        return sorted([aff for aff in self.affiliations], key=lambda k: k.position)

    def remove_affiliation(self, affiliation_id: str) -> None:
        for affiliation in self.affiliations:
            if affiliation.id == affiliation_id:
                self.affiliations.remove(affiliation)
                self.affiliations.reorder()
                return

    def add_email_address(self, email: str, primary: bool = False,
                          restricted: bool = False) -> None:
        for email_address in self.email_addresses:
            if email_address.email == email:
                email_address.restricted = restricted
                if primary:
                    self.email_addresses.remove(email_address)
                    self.email_addresses.insert(0, email_address)
                    self.email_addresses.reorder()
                return

        email_address = EmailAddress(email, restricted)
        if primary:
            self.email_addresses.insert(0, email_address)
        else:
            self.email_addresses.append(email_address)

        self.email_addresses.reorder()

    def remove_email_address(self, email: str) -> None:
        for email_address in self.email_addresses:
            if email_address.email == email:
                self.email_addresses.remove(email_address)
                self.email_addresses.reorder()
                return

    def __repr__(self) -> str:
        return '<Profile %r>' % self.id


class EmailAddress(db.Model):
    email = db.Column(db.Text(), primary_key=True)
    restricted = db.Column(db.Boolean(), nullable=False)
    profile_id = db.Column(db.String(ID_LENGTH), db.ForeignKey('profile.id'))
    profile = db.relationship('Profile', back_populates='email_addresses')
    position = db.Column(db.Integer())

    def __init__(self, email: str, restricted: bool = False) -> None:
        self.email = email
        self.restricted = restricted

    def __repr__(self) -> str:
        return '<EmailAddress %r>' % self.email
