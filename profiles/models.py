from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ID_LENGTH = 8


class Profile(db.Model):
    id = db.Column(db.String(ID_LENGTH), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    orcid = db.Column(db.String(19), unique=True)

    def __init__(self, profile_id: str, name: str, orcid: str = None) -> None:
        self.id = profile_id
        self.name = name
        self.orcid = orcid

    def __repr__(self) -> str:
        return '<Profile %r>' % self.id
