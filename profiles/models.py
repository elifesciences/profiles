from datetime import datetime, timezone
from typing import Optional, Type

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import types

db = SQLAlchemy()

ID_LENGTH = 8


class UTCDateTime(types.TypeDecorator):
    impl = types.DateTime

    def python_type(self) -> Type:
        return datetime

    def process_bind_param(self, value, dialect) -> Optional[datetime]:
        if value is not None:
            return value.astimezone(timezone.utc)

    def process_literal_param(self, value, dialect):
        raise NotImplementedError()

    def process_result_value(self, value, dialect) -> Optional[datetime]:
        if value is not None:
            return datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=timezone.utc)


class OrcidToken(db.Model):
    orcid = db.Column(db.String(19), primary_key=True)
    access_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(UTCDateTime, nullable=False)

    def __init__(self, orcid: str, access_token: str, expires_at: datetime) -> None:
        self.orcid = orcid
        self.access_token = access_token
        self.expires_at = expires_at

    def __repr__(self) -> str:
        return '<OrcidToken %r>' % self.orcid


class Profile(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    orcid = db.Column(db.String(19), unique=True)

    def __init__(self, profile_id: str, name: str, orcid: str = None) -> None:
        self.id = profile_id
        self.name = name
        self.orcid = orcid

    def __repr__(self) -> str:
        return '<Profile %r>' % self.id
