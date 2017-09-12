from flask_sqlalchemy import SQLAlchemy

from profiles.utilities import generate_id

db = SQLAlchemy()


class Profile(db.Model):
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    orcid = db.Column(db.String(19), unique=True)

    def __init__(self, name: str, orcid: str = None):
        self.id = generate_id()
        self.name = name
        self.orcid = orcid

    def __repr__(self):
        return '<Profile %r>' % self.id
