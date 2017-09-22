from datetime import datetime

from profiles.database import UTCDateTime, db

ID_LENGTH = 8


class OrcidToken(db.Model):
    orcid = db.Column(db.String(19), primary_key=True)
    access_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(UTCDateTime, nullable=False)

    def __init__(self, orcid: str, access_token: str, expires_at: datetime) -> None:
        self.orcid = orcid
        self.access_token = access_token
        self.expires_at = expires_at

    def __repr__(self) -> str:
        return '<OrcidToken for %r>' % self.orcid


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
