from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.orderinglist import ordering_list

db = SQLAlchemy()

ID_LENGTH = 8


class OrcidToken(db.Model):
    orcid = db.Column(db.String(19), primary_key=True)
    access_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime(), nullable=False)

    def __init__(self, orcid: str, access_token: str, expires_at: datetime) -> None:
        self.orcid = orcid
        self.access_token = access_token
        self.expires_at = expires_at


class Profile(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    orcid = db.Column(db.String(19), unique=True)
    email_addresses = db.relationship('EmailAddress', order_by='EmailAddress.position',
                                      collection_class=ordering_list('position'),
                                      cascade='all, delete-orphan', back_populates='profile')

    def __init__(self, profile_id: str, name: str, orcid: str = None) -> None:
        self.id = profile_id
        self.name = name
        self.orcid = orcid

    def update_from_orcid_record(self, orcid_record: dict):
        if 'name' in orcid_record['person']:
            self.name = '{} {}'.format(orcid_record['person']['name']['given-names']['value'],
                                       orcid_record['person']['name']['family-name']['value'])

        for email in self.email_addresses:
            found = False
            for orcid_email in orcid_record['person']['emails']['email'] or {}:
                if orcid_email['email'] == email.email:
                    found = True
                    break
            if not found:
                self.remove_email_address(email.email)

        for orcid_email in orcid_record['person']['emails']['email'] or {}:
            if orcid_email['verified']:
                self.add_email_address(orcid_email['email'], orcid_email['primary'],
                                       orcid_email['visibility'] != 'PUBLIC')

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

    def remove_email_address(self, email: str):
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
