from alembic import op
import sqlalchemy as sa

revision = 'f17777978680'
down_revision = '59a7cdca7cb0'
branch_labels = None
depends_on = None

orcid_token_helper = sa.Table(
    'orcid_token',
    sa.MetaData(),
)


def upgrade():
    connection = op.get_bind()

    connection.execute(orcid_token_helper.delete())


def downgrade():
    pass
