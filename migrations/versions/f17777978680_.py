from profiles.models import OrcidToken, db

revision = 'f17777978680'
down_revision = '59a7cdca7cb0'
branch_labels = None
depends_on = None


def upgrade():
    db.session.query(OrcidToken).delete()


def downgrade():
    pass
