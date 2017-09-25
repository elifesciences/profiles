import collections
import string
from abc import ABC, abstractmethod
from typing import Callable, List

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

    @abstractmethod
    def list(self, limit: int = None, offset: int = 0, desc: bool = True) -> List[Profile]:
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
    def __init__(self, db: SQLAlchemy, next_id_generator: Callable[[], str] = None) -> None:
        if next_id_generator is None:
            def generate_id():
                return generate_random_string(ID_LENGTH, string.ascii_lowercase + string.digits)

            next_id_generator = generate_id

        self.db = db
        self._next_id_generator = next_id_generator

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
        profile_id = self._next_id_generator()

        if self.db.session.query(Profile.id).filter_by(id=profile_id).scalar() is not None:
            raise RuntimeError('Generated ID already in use')

        return profile_id

    def list(self, limit: int = None, offset: int = 0, desc: bool = True) -> List[Profile]:
        query = self.db.session.query(Profile)

        if desc:
            query = query.order_by(Profile._index_name.desc())  # pylint: disable=protected-access
        else:
            query = query.order_by(Profile._index_name.asc())  # pylint: disable=protected-access

        return query.limit(limit).offset(offset).all()

    def __len__(self) -> int:
        return self.db.session.query(Profile).count()
