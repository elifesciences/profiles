import collections
import logging
import string
from abc import abstractmethod
from typing import Callable, List

from flask_sqlalchemy import SQLAlchemy
from retrying import retry
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from profiles.exceptions import OrcidTokenNotFound, ProfileNotFound
from profiles.models import EmailAddress, ID_LENGTH, OrcidToken, Profile
from profiles.types import CanBeCleared
from profiles.utilities import generate_random_string

LOGGER = logging.getLogger(__name__)


class OrcidTokens(CanBeCleared):
    @abstractmethod
    def add(self, orcid_token: OrcidToken) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, orcid: str) -> OrcidToken:
        raise NotImplementedError

    @abstractmethod
    def remove(self, orcid: str) -> None:
        raise NotImplementedError


class Profiles(CanBeCleared, collections.Sized):
    @abstractmethod
    def add(self, profile: Profile) -> Profile:
        raise NotImplementedError

    @abstractmethod
    def get(self, profile_id: str) -> Profile:
        raise NotImplementedError

    @abstractmethod
    def get_by_orcid(self, orcid: str) -> Profile:
        raise NotImplementedError

    @abstractmethod
    def get_by_email_address(self, *email_addresses: str) -> Profile:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def list(self, limit: int = None, offset: int = 0, desc: bool = False) -> List[Profile]:
        raise NotImplementedError


class SQLAlchemyOrcidTokens(OrcidTokens):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def add(self, orcid_token: OrcidToken) -> None:
        self.db.session.add(orcid_token)

    def get(self, orcid: str) -> OrcidToken:
        try:
            return self.db.session.query(OrcidToken).filter_by(orcid=orcid).one()
        except NoResultFound as exception:
            raise OrcidTokenNotFound('ORCID token for the ORCID {} not found'.format(orcid)) \
                from exception

    def clear(self) -> None:
        self.db.session.query(OrcidToken).delete()

    def remove(self, orcid: str) -> None:
        try:
            orcid_token = self.db.session.query(OrcidToken).filter_by(orcid=orcid).one()
            self.db.session.delete(orcid_token)
        except NoResultFound:
            pass


class SQLAlchemyProfiles(Profiles):
    def __init__(self, db: SQLAlchemy, next_id_generator: Callable[[], str] = None) -> None:
        if next_id_generator is None:
            def generate_id():
                return generate_random_string(ID_LENGTH, string.ascii_lowercase + string.digits)

            next_id_generator = generate_id

        self.db = db
        self._next_id_generator = next_id_generator

    def add(self, profile: Profile) -> Profile:
        self.db.session.add(profile)
        try:
            self.db.session.flush([profile])
        except IntegrityError as exception:
            self.db.session.rollback()

            if profile.orcid:
                LOGGER.info('Profile for ORCID %s appears to already exist', profile.orcid)
                try:
                    return self.get_by_orcid(profile.orcid)
                except NoResultFound:
                    LOGGER.error('Unable to fetch profile for ORCID %s', profile.orcid)

            raise exception

        return profile

    def get(self, profile_id: str) -> Profile:
        try:
            return self.db.session.query(Profile).filter_by(id=profile_id).one()
        except NoResultFound as exception:
            raise ProfileNotFound('Profile with the ID {} not found'.format(profile_id)) \
                from exception

    def get_by_orcid(self, orcid: str) -> Profile:
        try:
            return self.db.session.query(Profile).filter_by(orcid=orcid).one()
        except NoResultFound as exception:
            raise ProfileNotFound('Profile with the ORCID {} not found'.format(orcid)) \
                from exception

    def get_by_email_address(self, *email_addresses: str) -> Profile:
        if not email_addresses:
            raise ProfileNotFound('No email address(es) provided')

        try:
            return self.db.session.query(Profile).join(EmailAddress) \
                .filter(EmailAddress.email.in_(email_addresses)).one()
        except NoResultFound as exception:
            raise ProfileNotFound('Profile with the email address(es) {} not found'
                                  .format(email_addresses)) from exception

    @retry(stop_max_attempt_number=10)
    def next_id(self) -> str:
        profile_id = self._next_id_generator()

        if self.db.session.query(Profile.id).filter_by(id=profile_id).scalar() is not None:
            raise RuntimeError('Generated ID already in use')

        return profile_id

    def list(self, limit: int = None, offset: int = 0, desc: bool = True) -> List[Profile]:

        query = self.db.session.query(Profile)

        if desc:
            query = query.order_by(Profile.desc())
        else:
            query = query.order_by(Profile.asc())

        return query.limit(limit).offset(offset).all()

    def clear(self) -> None:
        self.db.session.query(Profile).delete()

    def __len__(self) -> int:
        return self.db.session.query(Profile).count()
