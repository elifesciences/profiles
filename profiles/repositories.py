import collections
import string
from abc import ABC, abstractmethod

from flask_sqlalchemy import SQLAlchemy
from retrying import retry
from sqlalchemy.orm.exc import NoResultFound

from profiles.exceptions import OrcidTokenNotFound, ProfileNotFound
from profiles.models import ID_LENGTH, OrcidToken, Profile
from profiles.utilities import generate_random_string


class OrcidTokens(ABC):
    @abstractmethod
    def add(self, orcid_token: OrcidToken) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, orcid: str) -> OrcidToken:
        raise NotImplementedError


class Profiles(ABC, collections.Sized):
    @abstractmethod
    def add(self, profile: Profile) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, profile_id: str) -> Profile:
        raise NotImplementedError

    @abstractmethod
    def get_by_orcid(self, orcid: str) -> Profile:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> str:
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


class SQLAlchemyProfiles(Profiles):
    def __init__(self, db: SQLAlchemy) -> None:
        self.db = db

    def add(self, profile: Profile) -> None:
        self.db.session.add(profile)

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

    @retry(stop_max_attempt_number=10)
    def next_id(self) -> str:
        profile_id = generate_random_string(ID_LENGTH, string.ascii_lowercase + string.digits)

        if self.db.session.query(Profile.id).filter_by(id=profile_id).scalar() is not None:
            raise RuntimeError('Generated ID already in use')

        return profile_id

    def __len__(self) -> int:
        return self.db.session.query(Profile).count()
